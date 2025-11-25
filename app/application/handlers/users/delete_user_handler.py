from dataclasses import dataclass
from uuid import UUID
from mediatr import GenericQuery

from app.application.ports.usecase import UseCase
from app.domain.repositories.user_repository import IUserRepository


@dataclass
class DeleteUserResponse:
    """Response for user deletion."""
    success: bool


@dataclass
class DeleteUserRequest(GenericQuery[DeleteUserResponse]):
    """Request for deleting a user."""
    user_id: UUID


class DeleteUserHandler(UseCase[DeleteUserRequest, DeleteUserResponse]):
    """Use case for deleting a user."""
    
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
    
    async def handle(self, request: DeleteUserRequest) -> DeleteUserResponse:
        success = await self.user_repository.delete(request.user_id)
        if not success:
            raise ValueError("User not found")
        return DeleteUserResponse(success=success)

