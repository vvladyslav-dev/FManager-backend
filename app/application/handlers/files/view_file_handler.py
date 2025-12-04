from pydantic import BaseModel
from mediatr import GenericQuery, Mediator
from dependency_injector.wiring import inject, Provide
from app.core.container import Container  # noqa: F401
from uuid import UUID

from app.application.ports.usecase import UseCase
from app.domain.repositories.file_repository import IFileRepository
from app.infrastructure.services.azure_storage import azure_storage_client
from typing import TYPE_CHECKING


class ViewFileResponse(BaseModel):
    """Response containing file data for viewing/downloading."""
    content: bytes
    content_type: str
    filename: str
    disposition: str  # "inline" or "attachment"


class ViewFileRequest(BaseModel, GenericQuery[ViewFileResponse]):
    """Request for viewing/downloading a file."""
    file_id: UUID


@Mediator.handler
class ViewFileHandler(UseCase[ViewFileRequest, ViewFileResponse]):
    """Use case for viewing/downloading a file by ID."""
    
    @inject
    def __init__(self, file_repository: IFileRepository = Provide[Container.file_repository]):
        self.file_repository = file_repository
    
    async def handle(self, request: ViewFileRequest) -> ViewFileResponse:
        # Get file record
        file_record = await self.file_repository.get_by_id(request.file_id)
        if not file_record:
            raise ValueError("File not found")
        
        # Download file from Azure Blob Storage
        blob_name = str(file_record.blob_name)
        file_content = await azure_storage_client.download_file(blob_name)
        
        # Determine content type
        content_type = str(file_record.content_type) if file_record.content_type is not None else "application/octet-stream"
        
        # For viewable files, use inline disposition; for others, use attachment
        viewable_types = [
            "application/pdf",
            "image/",
            "text/",
            "application/json",
        ]
        is_viewable = any(content_type.startswith(t) for t in viewable_types)
        disposition = "inline" if is_viewable else "attachment"
        
        return ViewFileResponse(
            content=file_content,
            content_type=content_type,
            filename=file_record.original_filename or "file",
            disposition=disposition
        )
