from pydantic import BaseModel
from mediatr import GenericQuery, Mediator
from dependency_injector.wiring import inject, Provide
from app.core.container import Container  # noqa: F401

from app.application.ports.usecase import UseCase
from app.domain.models import User
from app.domain.repositories.user_repository import IUserRepository
from app.core.auth import verify_password, create_access_token
from app.application.dto.models import UserDTO
from typing import TYPE_CHECKING


class LoginResponse(BaseModel):
    """Response containing access token and user."""
    access_token: str
    user: UserDTO
    token_type: str = "bearer"



class LoginRequest(BaseModel, GenericQuery[LoginResponse]):
    """Request for user login."""
    email: str
    password: str


@Mediator.handler
class LoginHandler(UseCase[LoginRequest, LoginResponse]):
    """Use case for user login."""
    
    @inject
    def __init__(self, user_repository: IUserRepository = Provide[Container.user_repository]):
        self.user_repository = user_repository
    
    async def handle(self, request: LoginRequest) -> LoginResponse:
        # Get user by email
        user = await self.user_repository.get_by_email(request.email)
        if not user:
            raise ValueError("Invalid email or password")
        
        # Check password
        if user.password_hash is None or not verify_password(request.password, str(user.password_hash)):
            raise ValueError("Invalid email or password")
        
        # Check if admin is approved (super admins can always login)
        # Use explicit boolean checks to avoid SQLAlchemy Column type issues
        if bool(user.is_admin) and not bool(user.is_super_admin) and not bool(user.is_approved):
            raise ValueError("Your registration is pending approval by a super administrator")
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
        
        return LoginResponse(
            access_token=access_token,
            user=UserDTO(
                id=user.id,
                name=user.name,
                email=user.email,
                is_admin=user.is_admin,
                is_super_admin=user.is_super_admin,
                is_approved=user.is_approved,
                admin_id=user.admin_id,
                avatar_url=getattr(user, 'avatar_url', None),
                created_at=getattr(user, 'created_at', None)
            )
        )

