from uuid import UUID
from pydantic import BaseModel
from mediatr import GenericQuery, Mediator
from dependency_injector.wiring import inject, Provide
from app.core.container import Container  # noqa: F401

from app.application.ports.usecase import UseCase
from app.domain.repositories.user_repository import IUserRepository
from app.infrastructure.services.azure_storage import azure_storage_client


class UploadAvatarResponse(BaseModel):
    avatar_url: str


class UploadAvatarRequest(BaseModel, GenericQuery[UploadAvatarResponse]):
    user_id: UUID
    filename: str
    content_type: str | None = None
    content: bytes
    file_size: int | None = None


@Mediator.handler
class UploadAvatarHandler(UseCase[UploadAvatarRequest, UploadAvatarResponse]):
    """Upload avatar for a user and update avatar_url."""

    MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB
    ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png"}

    @inject
    def __init__(
        self,
        user_repository: IUserRepository = Provide[Container.user_repository],
    ):
        self.user_repository = user_repository

    async def handle(self, request: UploadAvatarRequest) -> UploadAvatarResponse:
        # Validate file size
        if request.file_size and request.file_size > self.MAX_FILE_SIZE:
            raise ValueError("File too large (max 2MB)")
        
        # Validate content type
        if request.content_type and request.content_type not in self.ALLOWED_CONTENT_TYPES:
            raise ValueError("Unsupported file type. Only JPEG and PNG are allowed")
        
        user = await self.user_repository.get_by_id(request.user_id)
        if not user:
            raise ValueError("User not found")

        # Compose blob path
        blob_name = f"avatars/{str(request.user_id)}/{request.filename}"
        # Upload to storage
        blob_url = await azure_storage_client.upload_file(
            file_content=request.content,
            blob_name=blob_name,
        )

        user.avatar_url = blob_url
        await self.user_repository.update(user)

        return UploadAvatarResponse(avatar_url=blob_url)
