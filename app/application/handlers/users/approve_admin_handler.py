from uuid import UUID
from pydantic import BaseModel
from mediatr import GenericQuery, Mediator
from dependency_injector.wiring import inject, Provide

from app.application.ports.usecase import UseCase
from app.domain.models import User
from app.domain.repositories.user_repository import IUserRepository
from app.application.dto.models import UserDTO
from app.core.container import Container



class ApproveAdminResponse(BaseModel):
    """Response containing approved admin user."""
    user: UserDTO


class ApproveAdminRequest(BaseModel, GenericQuery[ApproveAdminResponse]):
    """Request for approving an admin user."""
    user_id: UUID


@Mediator.handler
class ApproveAdminHandler(UseCase[ApproveAdminRequest, ApproveAdminResponse]):
    """Use case for approving an admin user registration."""
    
    @inject
    def __init__(self, user_repository: IUserRepository = Provide[Container.user_repository]):
        self.user_repository = user_repository
    
    async def handle(self, request: ApproveAdminRequest) -> ApproveAdminResponse:
        # Get user
        user = await self.user_repository.get_by_id(request.user_id)
        if not user:
            raise ValueError("User not found")
        
        # Verify user is an admin
        # Use explicit boolean check to avoid SQLAlchemy Column type issues
        if not bool(user.is_admin):
            raise ValueError("User is not an admin")
        
        # Verify user is not a super admin (super admins don't need approval)
        if bool(user.is_super_admin):
            raise ValueError("Super admins do not need approval")
        
        # Approve the user
        # Use setattr to avoid type checker issues with SQLAlchemy Column assignment
        setattr(user, 'is_approved', True)
        updated_user = await self.user_repository.update(user)
        
        return ApproveAdminResponse(user=UserDTO(
            id=updated_user.id,
            name=updated_user.name,
            email=updated_user.email,
            is_admin=updated_user.is_admin,
            is_super_admin=updated_user.is_super_admin,
            is_approved=updated_user.is_approved,
            admin_id=updated_user.admin_id,
            created_at=getattr(updated_user, 'created_at', None)
        ))


