from dataclasses import dataclass
from uuid import UUID
from typing import List
from mediatr import GenericQuery

from app.application.ports.usecase import UseCase
from app.domain.models import User
from app.domain.repositories.user_repository import IUserRepository


@dataclass
class ListUsersByAdminResponse:
    """Response containing users for admin."""
    users: List[User]


@dataclass
class ListUsersByAdminRequest(GenericQuery[ListUsersByAdminResponse]):
    """Request for listing users by admin ID."""
    admin_id: UUID


class ListUsersByAdminHandler(UseCase[ListUsersByAdminRequest, ListUsersByAdminResponse]):
    """Use case for listing users by admin ID."""
    
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
    
    async def handle(self, request: ListUsersByAdminRequest) -> ListUsersByAdminResponse:
        users = await self.user_repository.get_by_admin_id(request.admin_id)
        return ListUsersByAdminResponse(users=users)

