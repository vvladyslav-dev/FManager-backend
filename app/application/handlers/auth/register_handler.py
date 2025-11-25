from dataclasses import dataclass
from uuid import uuid4
from mediatr import GenericQuery

from app.application.ports.usecase import UseCase
from app.domain.models import User
from app.domain.repositories.user_repository import IUserRepository
from app.core.auth import get_password_hash, create_access_token


@dataclass
class RegisterResponse:
    """Response containing access token and user."""
    access_token: str
    user: User
    token_type: str = "bearer"



@dataclass
class RegisterRequest(GenericQuery[RegisterResponse]):
    """Request for user registration."""
    email: str
    password: str
    name: str
    is_admin: bool = False


class RegisterHandler(UseCase[RegisterRequest, RegisterResponse]):
    """Use case for user registration."""
    
    def __init__(self, user_repository: IUserRepository):
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
                user=created_user
            )
        
        # Create access token for regular users
        access_token = create_access_token(data={"sub": str(created_user.id), "email": created_user.email})
        
        return RegisterResponse(
            access_token=access_token,
            user=created_user
        )

