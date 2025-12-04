from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from mediatr import GenericQuery, Mediator
from dependency_injector.wiring import inject, Provide
from app.core.container import Container  # noqa: F401

from app.application.ports.usecase import UseCase
from app.domain.models import FormSubmission
from app.domain.repositories.form_submission_repository import IFormSubmissionRepository
from app.application.dto.models import FormSubmissionDTO, FileDTO, FormFieldValueDTO, UserDTO, FormDTO, FormFieldDTO
from typing import TYPE_CHECKING


class GetSubmissionsByAdminResponse(BaseModel):
    """Response containing submissions for admin."""
    submissions: list[FormSubmissionDTO]


class GetSubmissionsByAdminRequest(BaseModel, GenericQuery[GetSubmissionsByAdminResponse]):
    """Request for getting submissions by admin ID."""
    admin_id: UUID
    skip: int = 0
    limit: int = 10
    date_from: datetime | None = None
    date_to: datetime | None = None
    user_name: str | None = None
    user_email: str | None = None
    field_value_search: str | None = None
    form_id: UUID | None = None


@Mediator.handler
class GetSubmissionsByAdminHandler(UseCase[GetSubmissionsByAdminRequest, GetSubmissionsByAdminResponse]):
    """Use case for getting submissions by admin ID."""
    
    @inject
    def __init__(self, submission_repository: IFormSubmissionRepository = Provide[Container.form_submission_repository]):
        self.submission_repository = submission_repository
    
    async def handle(self, request: GetSubmissionsByAdminRequest) -> GetSubmissionsByAdminResponse:
        submissions = await self.submission_repository.get_by_admin_id(
            request.admin_id,
            request.skip,
            request.limit,
            request.date_from,
            request.date_to,
            request.user_name,
            request.user_email,
            request.field_value_search,
            request.form_id
        )
        dto_list: list[FormSubmissionDTO] = []
        for s in submissions:
            dto_list.append(
                FormSubmissionDTO(
                    id=s.id,
                    form_id=s.form_id,
                    user_id=s.user_id,
                    submitted_at=s.submitted_at,
                    user=UserDTO(
                        id=s.user.id,
                        name=s.user.name,
                        email=s.user.email,
                        is_admin=s.user.is_admin,
                        is_super_admin=s.user.is_super_admin,
                        is_approved=s.user.is_approved,
                        admin_id=s.user.admin_id,
                        created_at=getattr(s.user, 'created_at', None)
                    ) if getattr(s, 'user', None) else None,
                    form=FormDTO(
                        id=s.form.id,
                        title=s.form.title,
                        description=s.form.description,
                        creator_id=s.form.creator_id,
                        created_at=getattr(s.form, 'created_at', None),
                        updated_at=getattr(s.form, 'updated_at', None),
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
                            ) for f in s.form.fields
                        ]
                    ) if getattr(s, 'form', None) else None,
                    field_values=[
                        FormFieldValueDTO(
                            id=v.id,
                            field_id=v.field_id,
                            value=v.value
                        ) for v in s.field_values
                    ],
                    files=[
                        FileDTO(
                            id=f.id,
                            field_id=f.field_id,
                            original_filename=f.original_filename,
                            blob_url=f.blob_url,
                            file_size=f.file_size,
                            content_type=f.content_type
                        ) for f in s.files
                    ]
                )
            )
        return GetSubmissionsByAdminResponse(submissions=dto_list)

