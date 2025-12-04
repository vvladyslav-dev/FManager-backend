from uuid import UUID
from pydantic import BaseModel
from mediatr import GenericQuery, Mediator
from dependency_injector.wiring import inject, Provide
from app.core.container import Container  # noqa: F401

from app.application.ports.usecase import UseCase
from app.domain.repositories.form_submission_repository import IFormSubmissionRepository
from typing import TYPE_CHECKING


class DeleteSubmissionResponse(BaseModel):
    """Response for submission deletion."""
    success: bool


class DeleteSubmissionRequest(BaseModel, GenericQuery[DeleteSubmissionResponse]):
    """Request for deleting a submission."""
    submission_id: UUID


@Mediator.handler
class DeleteSubmissionHandler(UseCase[DeleteSubmissionRequest, DeleteSubmissionResponse]):
    """Use case for deleting a submission."""
    
    @inject
    def __init__(self, submission_repository: IFormSubmissionRepository = Provide[Container.form_submission_repository]):
        self.submission_repository = submission_repository
    
    async def handle(self, request: DeleteSubmissionRequest) -> DeleteSubmissionResponse:
        success = await self.submission_repository.delete(request.submission_id)
        if not success:
            raise ValueError("Submission not found")
        return DeleteSubmissionResponse(success=success)

