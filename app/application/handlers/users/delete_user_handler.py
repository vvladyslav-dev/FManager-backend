from uuid import UUID
from pydantic import BaseModel
from mediatr import GenericQuery, Mediator
from dependency_injector.wiring import inject, Provide
from app.core.container import Container  # noqa: F401

from app.application.ports.usecase import UseCase
from app.domain.repositories.user_repository import IUserRepository


class DeleteUserResponse(BaseModel):
    """Response for user deletion."""
    success: bool


class DeleteUserRequest(BaseModel, GenericQuery[DeleteUserResponse]):
    """Request for deleting a user."""
    user_id: UUID


@Mediator.handler
class DeleteUserHandler(UseCase[DeleteUserRequest, DeleteUserResponse]):
    """Use case for deleting a user."""
    
    @inject
    def __init__(self, user_repository: IUserRepository = Provide[Container.user_repository]):
        self.user_repository = user_repository
    
    async def handle(self, request: DeleteUserRequest) -> DeleteUserResponse:
        success = await self.user_repository.delete(request.user_id)
        if not success:
            raise ValueError("User not found")
        return DeleteUserResponse(success=success)

