from dataclasses import dataclass, field
from uuid import UUID, uuid4
from typing import Dict, Any, Optional
from mediatr import GenericQuery
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.application.ports.usecase import UseCase
from app.domain.models import FormSubmission, FormFieldValue, User, File
from app.domain.repositories.user_repository import IUserRepository
from app.domain.repositories.form_repository import IFormRepository
from app.domain.repositories.form_submission_repository import IFormSubmissionRepository
from app.domain.repositories.file_repository import IFileRepository
from app.core.azure_storage import azure_storage_client
import mimetypes

logger = logging.getLogger(__name__)


@dataclass
class SubmitFormResponse:
    """Response containing form submission."""
    submission: FormSubmission


@dataclass
class SubmitFormRequest(GenericQuery[SubmitFormResponse]):
    """Request for submitting a form."""
    form_id: UUID
    user_name: str
    user_email: Optional[str] = None
    field_values: Dict[str, Any] = field(default_factory=dict)
    files: Optional[Dict[str, Any]] = None


class SubmitFormHandler(UseCase[SubmitFormRequest, SubmitFormResponse]):
    """Use case for submitting a form."""
    
    def __init__(
        self,
        user_repository: IUserRepository,
        form_repository: IFormRepository,
        submission_repository: IFormSubmissionRepository,
        file_repository: IFileRepository,
        session: AsyncSession
    ):
        self.user_repository = user_repository
        self.form_repository = form_repository
        self.submission_repository = submission_repository
        self.file_repository = file_repository
        self.session = session
    
    async def handle(self, request: SubmitFormRequest) -> SubmitFormResponse:
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
        if request.field_values:
            for field in form.fields:
                field_id_str = str(field.id)
                if field_id_str in request.field_values:
                    value = FormFieldValue(
                        id=uuid4(),
                        submission_id=submission.id,
                        field_id=field.id,
                        value=str(request.field_values[field_id_str])
                    )
                    submission.field_values.append(value)
        
        # Handle files
        if request.files:
            for field_id_str, file_data in request.files.items():
                try:
                    field_id = UUID(field_id_str)
                    # Find corresponding field
                    field = next((f for f in form.fields if f.id == field_id), None)
                    if not field:
                        logger.warning(f"Field {field_id_str} not found in form {form.id}")
                        continue
                    
                    # Upload file to Azure
                    file_content = file_data.get("content")
                    if not file_content:
                        logger.error(f"No file content for field {field_id_str}")
                        raise ValueError(f"No file content for field {field_id_str}")
                    
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
                except ValueError as e:
                    logger.error(f"Error processing file for field {field_id_str}: {str(e)}")
                except Exception as e:
                    logger.error(f"Error processing file for field {field_id_str}: {str(e)}")
                    raise ValueError(f"Error processing file: {str(e)}")
        
        created_submission = await self.submission_repository.create(submission)
        
        return SubmitFormResponse(submission=created_submission)

