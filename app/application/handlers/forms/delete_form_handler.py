from uuid import UUID
from pydantic import BaseModel
from mediatr import GenericQuery, Mediator
from dependency_injector.wiring import inject, Provide
from app.core.container import Container  # noqa: F401

from app.application.ports.usecase import UseCase
from app.domain.repositories.form_repository import IFormRepository



class DeleteFormResponse(BaseModel):
    """Response for form deletion."""
    success: bool


class DeleteFormRequest(BaseModel, GenericQuery[DeleteFormResponse]):
    """Request for deleting a form."""
    form_id: UUID


@Mediator.handler
class DeleteFormHandler(UseCase[DeleteFormRequest, DeleteFormResponse]):
    """Use case for deleting a form."""
    
    @inject
    def __init__(self, form_repository: IFormRepository = Provide[Container.form_repository]):
        self.form_repository = form_repository
    
    async def handle(self, request: DeleteFormRequest) -> DeleteFormResponse:
        success = await self.form_repository.delete(request.form_id)
        if not success:
            raise ValueError("Form not found")
        return DeleteFormResponse(success=success)

