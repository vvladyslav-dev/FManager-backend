from dataclasses import dataclass
from uuid import UUID
from typing import Optional
from mediatr import GenericQuery

from app.application.ports.usecase import UseCase
from app.domain.models import User
from app.domain.repositories.user_repository import IUserRepository


@dataclass
class UpdateUserResponse:
    """Response containing updated user."""
    user: User


@dataclass
class UpdateUserRequest(GenericQuery[UpdateUserResponse]):
    """Request for updating a user."""
    user_id: UUID
    name: Optional[str] = None
    email: Optional[str] = None
    is_admin: Optional[bool] = None


class UpdateUserHandler(UseCase[UpdateUserRequest, UpdateUserResponse]):
    """Use case for updating a user."""
    
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
    
    async def handle(self, request: UpdateUserRequest) -> UpdateUserResponse:
        user = await self.user_repository.get_by_id(request.user_id)
        if not user:
            raise ValueError("User not found")
        
        if request.name is not None:
            setattr(user, 'name', request.name)
        if request.email is not None:
            setattr(user, 'email', request.email)
        if request.is_admin is not None:
            setattr(user, 'is_admin', request.is_admin)
        
        updated_user = await self.user_repository.update(user)
        return UpdateUserResponse(user=updated_user)

