from uuid import UUID
from pydantic import BaseModel
from mediatr import GenericQuery, Mediator
from dependency_injector.wiring import inject, Provide
from app.core.container import Container  # noqa: F401

from app.application.ports.usecase import UseCase
from app.domain.models import User
from app.domain.repositories.user_repository import IUserRepository
from app.application.dto.models import UserDTO
from typing import TYPE_CHECKING


class UpdateUserResponse(BaseModel):
    """Response containing updated user."""
    user: UserDTO


class UpdateUserRequest(BaseModel, GenericQuery[UpdateUserResponse]):
    """Request for updating a user."""
    user_id: UUID
    name: str | None = None
    email: str | None = None
    is_admin: bool | None = None


@Mediator.handler
class UpdateUserHandler(UseCase[UpdateUserRequest, UpdateUserResponse]):
    """Use case for updating a user."""
    
    @inject
    def __init__(self, user_repository: IUserRepository = Provide[Container.user_repository]):
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
        return UpdateUserResponse(user=UserDTO(
            id=updated_user.id,
            name=updated_user.name,
            email=updated_user.email,
            is_admin=updated_user.is_admin,
            is_super_admin=updated_user.is_super_admin,
            is_approved=updated_user.is_approved,
            admin_id=updated_user.admin_id,
            created_at=getattr(updated_user, 'created_at', None)
        ))

