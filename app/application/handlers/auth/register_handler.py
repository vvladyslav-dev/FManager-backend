from uuid import uuid4
from pydantic import BaseModel
from mediatr import GenericQuery, Mediator
from dependency_injector.wiring import inject, Provide
from app.core.container import Container  # noqa: F401

from app.application.ports.usecase import UseCase
from app.domain.models import User
from app.domain.repositories.user_repository import IUserRepository
from app.core.auth import get_password_hash, create_access_token
from app.application.dto.models import UserDTO
from typing import TYPE_CHECKING


class RegisterResponse(BaseModel):
    """Response containing access token and user."""
    access_token: str
    user: UserDTO
    token_type: str = "bearer"



class RegisterRequest(BaseModel, GenericQuery[RegisterResponse]):
    """Request for user registration."""
    email: str
    password: str
    name: str
    is_admin: bool = False


@Mediator.handler
class RegisterHandler(UseCase[RegisterRequest, RegisterResponse]):
    """Use case for user registration."""
    
    @inject
    def __init__(self, user_repository: IUserRepository = Provide[Container.user_repository]):
        self.user_repository = user_repository
    
    async def handle(self, request: RegisterRequest) -> RegisterResponse:
        # Check if user already exists
        existing_user = await self.user_repository.get_by_email(request.email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Create new user
        # If registering as admin, set is_approved=False (needs super admin approval)
        # is_super_admin can only be set manually in DB
        user = User(
            id=uuid4(),
            email=request.email,
            name=request.name,
            password_hash=get_password_hash(request.password),
            is_admin=request.is_admin,
            is_super_admin=False,  # Can only be set manually in DB
            is_approved=True if not request.is_admin else False  # Admins need approval
        )
        
        created_user = await self.user_repository.create(user)
        
        # If admin, don't create token - they need approval first
        # Use explicit boolean checks to avoid SQLAlchemy Column type issues
        if bool(created_user.is_admin) and not bool(created_user.is_approved):
            # Return response without token - admin needs approval
            return RegisterResponse(
                access_token="",  # Empty token - admin cannot login yet
                user=UserDTO(
                    id=created_user.id,
                    name=created_user.name,
                    email=created_user.email,
                    is_admin=created_user.is_admin,
                    is_super_admin=created_user.is_super_admin,
                    is_approved=created_user.is_approved,
                    admin_id=created_user.admin_id,
                    avatar_url=getattr(created_user, 'avatar_url', None),
                    created_at=getattr(created_user, 'created_at', None)
                )
            )
        
        # Create access token for regular users
        access_token = create_access_token(data={"sub": str(created_user.id), "email": created_user.email})
        
        return RegisterResponse(
            access_token=access_token,
            user=UserDTO(
                id=created_user.id,
                name=created_user.name,
                email=created_user.email,
                is_admin=created_user.is_admin,
                is_super_admin=created_user.is_super_admin,
                is_approved=created_user.is_approved,
                admin_id=created_user.admin_id,
                avatar_url=getattr(created_user, 'avatar_url', None),
                created_at=getattr(created_user, 'created_at', None)
            )
        )

