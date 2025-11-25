from dataclasses import dataclass
from uuid import UUID
from mediatr import GenericQuery

from app.application.ports.usecase import UseCase
from app.domain.repositories.user_repository import IUserRepository


@dataclass
class RejectAdminResponse:
    """Response indicating success of rejection."""
    success: bool


@dataclass
class RejectAdminRequest(GenericQuery[RejectAdminResponse]):
    """Request for rejecting an admin user registration."""
    user_id: UUID


class RejectAdminHandler(UseCase[RejectAdminRequest, RejectAdminResponse]):
    """Use case for rejecting an admin user registration (deletes the user)."""
    
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
    
    async def handle(self, request: RejectAdminRequest) -> RejectAdminResponse:
        # Get user
        user = await self.user_repository.get_by_id(request.user_id)
        if not user:
            raise ValueError("User not found")
        
        # Verify user is an admin
        # Use explicit boolean check to avoid SQLAlchemy Column type issues
        if not bool(user.is_admin):
            raise ValueError("User is not an admin")
        
        # Verify user is not a super admin (cannot delete super admins)
        if bool(user.is_super_admin):
            raise ValueError("Cannot delete super admin")
        
        # Delete the user (reject registration)
        success = await self.user_repository.delete(request.user_id)
        
        return RejectAdminResponse(success=success)


