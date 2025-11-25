from dataclasses import dataclass
from uuid import UUID
from mediatr import GenericQuery

from app.application.ports.usecase import UseCase
from app.domain.models import User
from app.domain.repositories.user_repository import IUserRepository


@dataclass
class ApproveAdminResponse:
    """Response containing approved admin user."""
    user: User


@dataclass
class ApproveAdminRequest(GenericQuery[ApproveAdminResponse]):
    """Request for approving an admin user."""
    user_id: UUID


class ApproveAdminHandler(UseCase[ApproveAdminRequest, ApproveAdminResponse]):
    """Use case for approving an admin user registration."""
    
    def __init__(self, user_repository: IUserRepository):
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
        
        return ApproveAdminResponse(user=updated_user)


