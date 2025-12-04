from uuid import UUID
from pydantic import BaseModel
from mediatr import GenericQuery, Mediator
from dependency_injector.wiring import inject, Provide
from app.core.container import Container  # noqa: F401

from app.application.ports.usecase import UseCase
from app.domain.repositories.form_submission_repository import IFormSubmissionRepository
from app.application.dto.models import FormSubmissionDTO, FileDTO, FormFieldValueDTO, UserDTO, FormDTO, FormFieldDTO


class GetSubmissionResponse(BaseModel):
    submission: FormSubmissionDTO


class GetSubmissionRequest(BaseModel, GenericQuery[GetSubmissionResponse]):
    submission_id: UUID


@Mediator.handler
class GetSubmissionHandler(UseCase[GetSubmissionRequest, GetSubmissionResponse]):
    """Get a submission by ID with all details."""

    @inject
    def __init__(
        self,
        submission_repository: IFormSubmissionRepository = Provide[Container.form_submission_repository],
    ):
        self.submission_repository = submission_repository

    async def handle(self, request: GetSubmissionRequest) -> GetSubmissionResponse:
        submission = await self.submission_repository.get_by_id(request.submission_id)
        if not submission:
            raise ValueError("Submission not found")

        # Convert to DTO
        dto = FormSubmissionDTO(
            id=submission.id,
            form_id=submission.form_id,
            user_id=submission.user_id,
            submitted_at=submission.submitted_at,
            user=UserDTO(
                id=submission.user.id,
                name=submission.user.name,
                email=submission.user.email,
                is_admin=submission.user.is_admin,
                is_super_admin=submission.user.is_super_admin,
                is_approved=submission.user.is_approved,
                admin_id=submission.user.admin_id,
                created_at=getattr(submission.user, 'created_at', None)
            ) if getattr(submission, 'user', None) else None,
            form=FormDTO(
                id=submission.form.id,
                title=submission.form.title,
                description=submission.form.description,
                creator_id=submission.form.creator_id,
                created_at=getattr(submission.form, 'created_at', None),
                updated_at=getattr(submission.form, 'updated_at', None),
                fields=[
                    FormFieldDTO(
                        id=f.id,
                        field_type=f.field_type,
                        label=f.label,
                        name=f.name,
                        is_required=f.is_required,
                        order=f.order,
                        options=f.options,
                        placeholder=getattr(f, 'placeholder', None)
                    ) for f in submission.form.fields
                ]
            ) if getattr(submission, 'form', None) else None,
            field_values=[
                FormFieldValueDTO(
                    id=v.id,
                    field_id=v.field_id,
                    value=v.value
                ) for v in submission.field_values
            ],
            files=[
                FileDTO(
                    id=f.id,
                    field_id=f.field_id,
                    original_filename=f.original_filename,
                    blob_url=f.blob_url,
                    file_size=f.file_size,
                    content_type=f.content_type
                ) for f in submission.files
            ]
        )

        return GetSubmissionResponse(submission=dto)
