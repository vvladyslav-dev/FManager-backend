from dataclasses import dataclass
from typing import List
from mediatr import GenericQuery

from app.application.ports.usecase import UseCase
from app.domain.models import User
from app.domain.repositories.user_repository import IUserRepository


@dataclass
class GetUnapprovedAdminsResponse:
    """Response containing list of unapproved admin users."""
    admins: List[User]


@dataclass
class GetUnapprovedAdminsRequest(GenericQuery[GetUnapprovedAdminsResponse]):
    """Request for getting unapproved admin users."""
    pass


class GetUnapprovedAdminsHandler(UseCase[GetUnapprovedAdminsRequest, GetUnapprovedAdminsResponse]):
    """Use case for getting all unapproved admin users."""
    
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
    
    async def handle(self, request: GetUnapprovedAdminsRequest) -> GetUnapprovedAdminsResponse:
        admins = await self.user_repository.get_unapproved_admins()
        return GetUnapprovedAdminsResponse(admins=admins)


