from uuid import UUID, uuid4
from pydantic import BaseModel
from mediatr import GenericQuery, Mediator
from dependency_injector.wiring import inject, Provide
from app.core.container import Container  # noqa: F401

from app.application.ports.usecase import UseCase
from app.domain.models import User
from app.domain.repositories.user_repository import IUserRepository
from app.application.dto.models import UserDTO
from typing import TYPE_CHECKING


class CreateUserResponse(BaseModel):
    """Response containing created user."""
    user: UserDTO


class CreateUserRequest(BaseModel, GenericQuery[CreateUserResponse]):
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
    email: str | None = None
    is_admin: bool = False
    admin_id: UUID | None = None


@Mediator.handler
class CreateUserHandler(UseCase[CreateUserRequest, CreateUserResponse]):
    """Use case for creating a new user.
    
    This handler creates a user and optionally links them to an administrator.
    The admin_id field enables multi-tenant data isolation.
    """
    
    @inject
    def __init__(self, user_repository: IUserRepository = Provide[Container.user_repository]):
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
        return CreateUserResponse(
            user=UserDTO(
                id=created_user.id,
                name=created_user.name,
                email=created_user.email,
                is_admin=created_user.is_admin,
                is_super_admin=created_user.is_super_admin,
                is_approved=created_user.is_approved,
                admin_id=created_user.admin_id,
                created_at=getattr(created_user, 'created_at', None)
            )
        )

