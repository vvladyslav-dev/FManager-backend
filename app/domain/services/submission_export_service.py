from abc import ABC, abstractmethod
from io import BytesIO
from typing import Literal
from uuid import UUID
from app.domain.models import FormSubmission


ExportFormat = Literal["csv", "xlsx"]


class ISubmissionExportService(ABC):
    """Interface for submission export service."""
    
    @abstractmethod
    async def export_submission(
        self, 
        submission: FormSubmission, 
        format: ExportFormat,
        locale: str = "en"
    ) -> tuple[BytesIO, str]:
        """
        Export submission to specified format.
        
        Args:
            submission: The form submission to export
            format: Export format (csv or xlsx)
            
        Returns:
            Tuple of (file buffer, filename)
        """
        pass
