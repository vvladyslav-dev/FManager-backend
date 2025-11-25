from dataclasses import dataclass
from uuid import UUID
from typing import Optional
from mediatr import GenericQuery

from app.application.ports.usecase import UseCase
from app.domain.models import User
from app.domain.repositories.user_repository import IUserRepository


@dataclass
class GetUserResponse:
    """Response containing user."""
    user: Optional[User]


@dataclass
class GetUserRequest(GenericQuery[GetUserResponse]):
    """Request for getting a user by ID."""
    user_id: UUID


class GetUserHandler(UseCase[GetUserRequest, GetUserResponse]):
    """Use case for getting a user by ID."""
    
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
    
    async def handle(self, request: GetUserRequest) -> GetUserResponse:
        user = await self.user_repository.get_by_id(request.user_id)
        return GetUserResponse(user=user)

