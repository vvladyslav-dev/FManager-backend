from uuid import UUID
from pydantic import BaseModel
from mediatr import GenericQuery, Mediator
from dependency_injector.wiring import inject, Provide
from app.core.container import Container  # noqa: F401

from app.application.ports.usecase import UseCase
from app.domain.repositories.form_submission_repository import IFormSubmissionRepository
from typing import TYPE_CHECKING


class GetSubmissionCountResponse(BaseModel):
    """Response containing submission count."""
    count: int


class GetSubmissionCountRequest(BaseModel, GenericQuery[GetSubmissionCountResponse]):
    """Request for getting submission count by form ID."""
    form_id: UUID


@Mediator.handler
class GetSubmissionCountHandler(UseCase[GetSubmissionCountRequest, GetSubmissionCountResponse]):
    """Use case for getting submission count by form ID."""
    
    @inject
    def __init__(self, submission_repository: IFormSubmissionRepository = Provide[Container.form_submission_repository]):
        self.submission_repository = submission_repository
    
    async def handle(self, request: GetSubmissionCountRequest) -> GetSubmissionCountResponse:
        count = await self.submission_repository.count_by_form_id(request.form_id)
        return GetSubmissionCountResponse(count=count)
