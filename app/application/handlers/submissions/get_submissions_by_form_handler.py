from dataclasses import dataclass
from uuid import UUID
from typing import List
from mediatr import GenericQuery

from app.application.ports.usecase import UseCase
from app.domain.models import FormSubmission
from app.domain.repositories.form_submission_repository import IFormSubmissionRepository


@dataclass
class GetSubmissionsByFormResponse:
    """Response containing submissions for form."""
    submissions: List[FormSubmission]


@dataclass
class GetSubmissionsByFormRequest(GenericQuery[GetSubmissionsByFormResponse]):
    """Request for getting submissions by form ID."""
    form_id: UUID


class GetSubmissionsByFormHandler(UseCase[GetSubmissionsByFormRequest, GetSubmissionsByFormResponse]):
    """Use case for getting submissions by form ID."""
    
    def __init__(self, submission_repository: IFormSubmissionRepository):
        self.submission_repository = submission_repository
    
    async def handle(self, request: GetSubmissionsByFormRequest) -> GetSubmissionsByFormResponse:
        submissions = await self.submission_repository.get_by_form_id(request.form_id)
        return GetSubmissionsByFormResponse(submissions=submissions)

