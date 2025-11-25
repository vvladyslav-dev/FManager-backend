from dataclasses import dataclass
from uuid import UUID, uuid4
from typing import Optional
from mediatr import GenericQuery

from app.application.ports.usecase import UseCase
from app.domain.models import User
from app.domain.repositories.user_repository import IUserRepository


@dataclass
class CreateUserResponse:
    """Response containing created user."""
    user: User


@dataclass
class CreateUserRequest(GenericQuery[CreateUserResponse]):
    """Request for creating a new user.
    
    Use case: Creates a new user in the system.
    
    admin_id is used to link the user to a specific administrator.
    This enables data isolation - each admin sees only their own users and forms.
    
    Example scenario:
    - Admin (dental technician) creates forms
    - User (doctor) fills out forms
    - Admin sees only their own doctors and their form submissions
    
    If admin_id is provided:
    - The user will be linked to that administrator
    - The admin can see this user via GET /admin/{admin_id}/users
    - The admin can see this user's submissions via GET /admin/{admin_id}/submissions
    
    If admin_id is None:
    - The user is not linked to any admin (standalone user)
    - Useful for creating top-level administrators (is_admin=True)
    """
    name: str
    email: Optional[str] = None
    is_admin: bool = False
    admin_id: Optional[UUID] = None


class CreateUserHandler(UseCase[CreateUserRequest, CreateUserResponse]):
    """Use case for creating a new user.
    
    This handler creates a user and optionally links them to an administrator.
    The admin_id field enables multi-tenant data isolation.
    """
    
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
    
    async def handle(self, request: CreateUserRequest) -> CreateUserResponse:
        # Validate admin_id if provided - ensures the admin exists and is actually an admin
        if request.admin_id:
            admin = await self.user_repository.get_by_id(request.admin_id)
            if not admin:
                raise ValueError(f"Admin with id {request.admin_id} not found")
            if admin.is_admin is False:
                raise ValueError(f"User with id {request.admin_id} is not an admin")
        
        user = User(
            id=uuid4(),
            name=request.name,
            email=request.email,
            is_admin=request.is_admin,
            is_super_admin=False,  # Can only be set manually in DB
            is_approved=True if not request.is_admin else False,  # Admins need approval
            admin_id=request.admin_id  # Links user to administrator for data isolation
        )
        created_user = await self.user_repository.create(user)
        return CreateUserResponse(user=created_user)

