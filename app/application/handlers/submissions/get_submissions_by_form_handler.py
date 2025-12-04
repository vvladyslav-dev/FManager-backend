from uuid import UUID
from pydantic import BaseModel
from mediatr import GenericQuery, Mediator
from dependency_injector.wiring import inject, Provide
from app.core.container import Container  # noqa: F401

from app.application.ports.usecase import UseCase
from app.domain.models import FormSubmission
from app.domain.repositories.form_submission_repository import IFormSubmissionRepository
from app.application.dto.models import FormSubmissionDTO, FileDTO, FormFieldValueDTO
from typing import TYPE_CHECKING


class GetSubmissionsByFormResponse(BaseModel):
    """Response containing submissions for form."""
    submissions: list[FormSubmissionDTO]


class GetSubmissionsByFormRequest(BaseModel, GenericQuery[GetSubmissionsByFormResponse]):
    """Request for getting submissions by form ID."""
    form_id: UUID


@Mediator.handler
class GetSubmissionsByFormHandler(UseCase[GetSubmissionsByFormRequest, GetSubmissionsByFormResponse]):
    """Use case for getting submissions by form ID."""
    
    @inject
    def __init__(self, submission_repository: IFormSubmissionRepository = Provide[Container.form_submission_repository]):
        self.submission_repository = submission_repository
    
    async def handle(self, request: GetSubmissionsByFormRequest) -> GetSubmissionsByFormResponse:
        submissions = await self.submission_repository.get_by_form_id(request.form_id)
        dto_list: list[FormSubmissionDTO] = []
        for s in submissions:
            dto_list.append(
                FormSubmissionDTO(
                    id=s.id,
                    form_id=s.form_id,
                    user_id=s.user_id,
                    submitted_at=s.submitted_at,
                    user=None,
                    form=None,
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
        return GetSubmissionsByFormResponse(submissions=dto_list)

