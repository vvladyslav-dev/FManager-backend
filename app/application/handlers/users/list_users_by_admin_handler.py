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


class ListUsersByAdminResponse(BaseModel):
    """Response containing users for admin."""
    users: list[UserDTO]


class ListUsersByAdminRequest(BaseModel, GenericQuery[ListUsersByAdminResponse]):
    """Request for listing users by admin ID."""
    admin_id: UUID


@Mediator.handler
class ListUsersByAdminHandler(UseCase[ListUsersByAdminRequest, ListUsersByAdminResponse]):
    """Use case for listing users by admin ID."""
    
    @inject
    def __init__(self, user_repository: IUserRepository = Provide[Container.user_repository]):
        self.user_repository = user_repository
    
    async def handle(self, request: ListUsersByAdminRequest) -> ListUsersByAdminResponse:
        users = await self.user_repository.get_by_admin_id(request.admin_id)
        return ListUsersByAdminResponse(users=[
            UserDTO(
                id=u.id,
                name=u.name,
                email=u.email,
                is_admin=u.is_admin,
                is_super_admin=u.is_super_admin,
                is_approved=u.is_approved,
                admin_id=u.admin_id,
                created_at=getattr(u, 'created_at', None)
            ) for u in users
        ])

