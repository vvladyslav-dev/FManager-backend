from pydantic import BaseModel, Field
from mediatr import GenericQuery, Mediator
from dependency_injector.wiring import inject, Provide
from app.core.container import Container  # noqa: F401

from app.application.ports.usecase import UseCase
from app.domain.repositories.user_repository import IUserRepository
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class ChangePasswordResponse(BaseModel):
    success: bool


class ChangePasswordRequest(BaseModel, GenericQuery[ChangePasswordResponse]):
    user_id: str = Field(..., description="User ID (UUID)")
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., description="New password")


@Mediator.handler
class ChangePasswordHandler(UseCase[ChangePasswordRequest, ChangePasswordResponse]):
    """Use case to change a user's password."""

    @inject
    def __init__(self, user_repository: IUserRepository = Provide[Container.user_repository]):
        self.user_repository = user_repository

    async def handle(self, request: ChangePasswordRequest) -> ChangePasswordResponse:
        user = await self.user_repository.get_by_id(request.user_id)
        if not user:
            raise ValueError("User not found")

        # Ensure user has a password set
        if not user.password_hash:
            raise ValueError("Password not set for user")

        # Verify current password
        if not pwd_context.verify(request.current_password, user.password_hash):
            raise ValueError("Invalid current password")

        # Update to new password
        user.password_hash = pwd_context.hash(request.new_password)
        await self.user_repository.update(user)

        return ChangePasswordResponse(success=True)
