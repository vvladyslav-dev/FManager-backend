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


class GetUserResponse(BaseModel):
    """Response containing user."""
    user: UserDTO | None


class GetUserRequest(BaseModel, GenericQuery[GetUserResponse]):
    """Request for getting a user by ID."""
    user_id: UUID


@Mediator.handler
class GetUserHandler(UseCase[GetUserRequest, GetUserResponse]):
    """Use case for getting a user by ID."""
    
    @inject
    def __init__(self, user_repository: IUserRepository = Provide[Container.user_repository]):
        self.user_repository = user_repository
    
    async def handle(self, request: GetUserRequest) -> GetUserResponse:
        user = await self.user_repository.get_by_id(request.user_id)
        if not user:
            return GetUserResponse(user=None)
        return GetUserResponse(
            user=UserDTO(
                id=user.id,
                name=user.name,
                email=user.email,
                is_admin=user.is_admin,
                is_super_admin=user.is_super_admin,
                is_approved=user.is_approved,
                admin_id=user.admin_id,
                created_at=getattr(user, 'created_at', None)
            )
        )

