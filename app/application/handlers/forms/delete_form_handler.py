from dataclasses import dataclass
from uuid import UUID
from mediatr import GenericQuery

from app.application.ports.usecase import UseCase
from app.domain.repositories.form_repository import IFormRepository


@dataclass
class DeleteFormResponse:
    """Response for form deletion."""
    success: bool


@dataclass
class DeleteFormRequest(GenericQuery[DeleteFormResponse]):
    """Request for deleting a form."""
    form_id: UUID


class DeleteFormHandler(UseCase[DeleteFormRequest, DeleteFormResponse]):
    """Use case for deleting a form."""
    
    def __init__(self, form_repository: IFormRepository):
        self.form_repository = form_repository
    
    async def handle(self, request: DeleteFormRequest) -> DeleteFormResponse:
        success = await self.form_repository.delete(request.form_id)
        if not success:
            raise ValueError("Form not found")
        return DeleteFormResponse(success=success)

