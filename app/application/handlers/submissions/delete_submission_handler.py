from dataclasses import dataclass
from uuid import UUID
from mediatr import GenericQuery

from app.application.ports.usecase import UseCase
from app.domain.repositories.form_submission_repository import IFormSubmissionRepository


@dataclass
class DeleteSubmissionResponse:
    """Response for submission deletion."""
    success: bool


@dataclass
class DeleteSubmissionRequest(GenericQuery[DeleteSubmissionResponse]):
    """Request for deleting a submission."""
    submission_id: UUID


class DeleteSubmissionHandler(UseCase[DeleteSubmissionRequest, DeleteSubmissionResponse]):
    """Use case for deleting a submission."""
    
    def __init__(self, submission_repository: IFormSubmissionRepository):
        self.submission_repository = submission_repository
    
    async def handle(self, request: DeleteSubmissionRequest) -> DeleteSubmissionResponse:
        success = await self.submission_repository.delete(request.submission_id)
        if not success:
            raise ValueError("Submission not found")
        return DeleteSubmissionResponse(success=success)

