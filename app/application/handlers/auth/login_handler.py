from dataclasses import dataclass
from mediatr import GenericQuery

from app.application.ports.usecase import UseCase
from app.domain.models import User
from app.domain.repositories.user_repository import IUserRepository
from app.core.auth import verify_password, create_access_token


@dataclass
class LoginResponse:
    """Response containing access token and user."""
    access_token: str
    user: User
    token_type: str = "bearer"



@dataclass
class LoginRequest(GenericQuery[LoginResponse]):
    """Request for user login."""
    email: str
    password: str


class LoginHandler(UseCase[LoginRequest, LoginResponse]):
    """Use case for user login."""
    
    def __init__(self, user_repository: IUserRepository):
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
            user=user
        )

