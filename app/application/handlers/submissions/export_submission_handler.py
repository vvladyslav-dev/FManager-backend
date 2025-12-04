from pydantic import BaseModel
from mediatr import GenericQuery, Mediator
from dependency_injector.wiring import inject, Provide
from io import BytesIO
from uuid import UUID

from app.application.ports.usecase import UseCase
from app.domain.repositories.form_submission_repository import IFormSubmissionRepository
from app.domain.services.submission_export_service import ISubmissionExportService, ExportFormat
from app.core.container import Container  # noqa: F401


class ExportSubmissionResponse(BaseModel):
    """Response containing exported submission file."""
    file_buffer: BytesIO
    filename: str
    media_type: str
    
    class Config:
        arbitrary_types_allowed = True


class ExportSubmissionRequest(BaseModel, GenericQuery[ExportSubmissionResponse]):
    """Request for exporting a submission."""
    submission_id: UUID
    format: ExportFormat
    locale: str = "en"


@Mediator.handler
class ExportSubmissionHandler(UseCase[ExportSubmissionRequest, ExportSubmissionResponse]):
    """Use case for exporting a submission to CSV or XLSX."""
    
    @inject
    def __init__(
        self,
        submission_repository: IFormSubmissionRepository = Provide[Container.form_submission_repository],
        export_service: ISubmissionExportService = Provide[Container.submission_export_service],
    ):
        self.submission_repository = submission_repository
        self.export_service = export_service
    
    async def handle(self, request: ExportSubmissionRequest) -> ExportSubmissionResponse:
        """Handle export submission request."""
        # Get submission with all related data
        submission = await self.submission_repository.get_by_id(request.submission_id)
        
        if not submission:
            raise ValueError(f"Submission with id {request.submission_id} not found")
        
        # Export submission
        file_buffer, filename = await self.export_service.export_submission(
            submission, 
            request.format,
            request.locale
        )
        
        # Determine media type based on format
        media_type = "text/csv" if request.format == "csv" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        
        return ExportSubmissionResponse(
            file_buffer=file_buffer,
            filename=filename,
            media_type=media_type
        )
