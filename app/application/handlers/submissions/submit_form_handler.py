from uuid import UUID, uuid4
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import json
from pydantic import BaseModel
from mediatr import GenericQuery, Mediator
from dependency_injector.wiring import inject, Provide
from app.core.container import Container  # noqa: F401

from app.application.ports.usecase import UseCase
from app.domain.models import FormSubmission, FormFieldValue, User, File
from app.domain.repositories.user_repository import IUserRepository
from app.domain.repositories.form_repository import IFormRepository
from app.domain.repositories.form_submission_repository import IFormSubmissionRepository
from app.domain.repositories.file_repository import IFileRepository
from app.infrastructure.services.azure_storage import azure_storage_client
from app.domain.events.event_bus import EventBus
from app.domain.events.submission_events import SubmissionCreatedEvent
import mimetypes
from app.application.dto.models import FormSubmissionDTO, FileDTO, FormFieldValueDTO

logger = logging.getLogger(__name__)


class SubmitFormResponse(BaseModel):
    """Response containing form submission."""
    submission: FormSubmissionDTO


class SubmitFormRequest(BaseModel, GenericQuery[SubmitFormResponse]):
    """Request for submitting a form."""
    form_id: UUID
    user_name: str
    user_email: str | None = None
    field_values_json: str | None = None
    file_fields_json: str | None = None
    # will hold starlette UploadFile objects; allow arbitrary types
    files: list[Any] | None = None

    class Config:
        arbitrary_types_allowed = True


@Mediator.handler
class SubmitFormHandler(UseCase[SubmitFormRequest, SubmitFormResponse]):
    """Use case for submitting a form."""
    
    @inject
    def __init__(
        self,
        user_repository: IUserRepository = Provide[Container.user_repository],
        form_repository: IFormRepository = Provide[Container.form_repository],
        submission_repository: IFormSubmissionRepository = Provide[Container.form_submission_repository],
        file_repository: IFileRepository = Provide[Container.file_repository],
        session: AsyncSession = Provide[Container.db_session],
        event_bus: EventBus = Provide[Container.event_bus]
    ):
        self.user_repository = user_repository
        self.form_repository = form_repository
        self.submission_repository = submission_repository
        self.file_repository = file_repository
        self.session = session
        self.event_bus = event_bus
    
    async def handle(self, request: SubmitFormRequest) -> SubmitFormResponse:
        # Debug logging
        logger.info(f"SubmitFormRequest: form_id={request.form_id}, user_name={request.user_name}")
        logger.info(f"field_values_json: {request.field_values_json}")
        logger.info(f"file_fields_json: {request.file_fields_json}")
        logger.info(f"files count: {len(request.files) if request.files else 0}")
        
        # Parse field_values JSON
        try:
            field_values_dict = json.loads(request.field_values_json) if request.field_values_json else {}
        except json.JSONDecodeError:
            raise ValueError("Invalid field_values JSON")
        
        # Parse and process files
        files_dict = {}
        if request.files and request.file_fields_json:
            try:
                file_fields_dict = json.loads(request.file_fields_json)
                for idx, file in enumerate(request.files):
                    field_id_str = file_fields_dict.get(str(idx))
                    if field_id_str:
                        content = await file.read()
                        files_dict.setdefault(field_id_str, []).append({
                            "content": content,
                            "filename": file.filename or "file"
                        })
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid file_fields JSON: {str(e)}")
        elif request.files and not request.file_fields_json:
            logger.error(f"Files provided but no file_fields_json. Files: {[f.filename for f in request.files]}")
            raise ValueError("file_fields mapping is required when files are uploaded")
        
        # Get form
        form = await self.form_repository.get_by_id(request.form_id)
        if not form:
            raise ValueError("Form not found")
        
        # Create or get user
        user = None
        if request.user_email:
            user = await self.user_repository.get_by_email(request.user_email)
        
        if not user:
            user = User(
                id=uuid4(),
                name=request.user_name,
                email=request.user_email,
                is_admin=False,
                is_super_admin=False,
                is_approved=True,  # Regular users don't need approval
                admin_id=form.creator_id  # Link to form creator
            )
            user = await self.user_repository.create(user)
        
        # Create submission
        submission = FormSubmission(
            id=uuid4(),
            form_id=request.form_id,
            user_id=user.id
        )
        
        # Create field values
        if field_values_dict:
            for field in form.fields:
                field_id_str = str(field.id)
                if field_id_str in field_values_dict:
                    value = FormFieldValue(
                        id=uuid4(),
                        submission_id=submission.id,
                        field_id=field.id,
                        value=str(field_values_dict[field_id_str])
                    )
                    submission.field_values.append(value)
        
        # Handle files
        if files_dict:
            for field_id_str, files_list in files_dict.items():
                try:
                    field_id = UUID(field_id_str)
                    # Find corresponding field
                    field = next((f for f in form.fields if f.id == field_id), None)
                    if not field:
                        logger.warning(f"Field {field_id_str} not found in form {form.id}")
                        continue
                    
                    for file_data in files_list:
                        try:
                            # Upload file to Azure
                            file_content = file_data.get("content")
                            if not file_content:
                                logger.error(f"No file content for field {field_id_str}")
                                continue
                            
                            original_filename = file_data.get("filename", "file")
                            blob_name = f"{submission.id}/{field_id}/{uuid4()}/{original_filename}"
                            
                            try:
                                blob_url = await azure_storage_client.upload_file(
                                    file_content,
                                    blob_name
                                )
                            except Exception as e:
                                logger.error(f"Failed to upload file to Azure: {str(e)}")
                                raise ValueError(f"Failed to upload file: {str(e)}")
                            
                            # Create file record
                            file_record = File(
                                id=uuid4(),
                                submission_id=submission.id,
                                field_id=field_id,
                                original_filename=original_filename,
                                blob_name=blob_name,
                                blob_url=blob_url,
                                file_size=len(file_content),
                                content_type=mimetypes.guess_type(original_filename)[0]
                            )
                            submission.files.append(file_record)
                        except Exception as e:
                            logger.error(f"Error processing file for field {field_id_str}: {str(e)}")
                            raise ValueError(f"Error processing file: {str(e)}")
                            
                except ValueError as e:
                    logger.error(f"Error processing files for field {field_id_str}: {str(e)}")
                except Exception as e:
                    logger.error(f"Error processing files for field {field_id_str}: {str(e)}")
                    raise ValueError(f"Error processing files: {str(e)}")
        
        created_submission = await self.submission_repository.create(submission)
        
        # Publish event for notification
        # Note: Transaction is automatically committed by middleware for POST requests
        event = SubmissionCreatedEvent(
            submission_id=created_submission.id,
            form_id=created_submission.form_id,
            user_id=created_submission.user_id
        )
        await self.event_bus.publish(event)
        
        return SubmitFormResponse(
            submission=FormSubmissionDTO(
                id=created_submission.id,
                form_id=created_submission.form_id,
                user_id=created_submission.user_id,
                submitted_at=created_submission.submitted_at,
                field_values=[
                    FormFieldValueDTO(
                        id=v.id,
                        field_id=v.field_id,
                        value=v.value
                    ) for v in created_submission.field_values
                ],
                files=[
                    FileDTO(
                        id=f.id,
                        field_id=f.field_id,
                        original_filename=f.original_filename,
                        blob_url=f.blob_url,
                        file_size=f.file_size,
                        content_type=f.content_type
                    ) for f in created_submission.files
                ]
            )
        )

