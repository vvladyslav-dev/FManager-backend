from pydantic import BaseModel
from mediatr import GenericQuery, Mediator
from dependency_injector.wiring import inject, Provide

from app.application.ports.usecase import UseCase
from app.domain.models import User
from app.domain.repositories.user_repository import IUserRepository
from app.application.dto.models import UserDTO
from app.core.container import Container  


class GetUnapprovedAdminsResponse(BaseModel):
    """Response containing list of unapproved admin users."""
    admins: list[UserDTO]


class GetUnapprovedAdminsRequest(BaseModel, GenericQuery[GetUnapprovedAdminsResponse]):
    """Request for getting unapproved admin users."""
    pass


@Mediator.handler
class GetUnapprovedAdminsHandler(UseCase[GetUnapprovedAdminsRequest, GetUnapprovedAdminsResponse]):
    """Use case for getting all unapproved admin users."""
    
    @inject
    def __init__(self, user_repository: IUserRepository = Provide[Container.user_repository]):
        self.user_repository = user_repository
    
    async def handle(self, request: GetUnapprovedAdminsRequest) -> GetUnapprovedAdminsResponse:
        admins = await self.user_repository.get_unapproved_admins()
        return GetUnapprovedAdminsResponse(admins=[
            UserDTO(
                id=u.id,
                name=u.name,
                email=u.email,
                is_admin=u.is_admin,
                is_super_admin=u.is_super_admin,
                is_approved=u.is_approved,
                admin_id=u.admin_id,
                created_at=getattr(u, 'created_at', None)
            ) for u in admins
        ])


