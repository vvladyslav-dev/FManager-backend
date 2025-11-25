from dataclasses import dataclass
from uuid import UUID
from typing import List, Optional
from datetime import datetime
from mediatr import GenericQuery

from app.application.ports.usecase import UseCase
from app.domain.models import FormSubmission
from app.domain.repositories.form_submission_repository import IFormSubmissionRepository


@dataclass
class GetSubmissionsByAdminResponse:
    """Response containing submissions for admin."""
    submissions: List[FormSubmission]


@dataclass
class GetSubmissionsByAdminRequest(GenericQuery[GetSubmissionsByAdminResponse]):
    """Request for getting submissions by admin ID."""
    admin_id: UUID
    skip: int = 0
    limit: int = 10
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    field_value_search: Optional[str] = None
    form_id: Optional[UUID] = None


class GetSubmissionsByAdminHandler(UseCase[GetSubmissionsByAdminRequest, GetSubmissionsByAdminResponse]):
    """Use case for getting submissions by admin ID."""
    
    def __init__(self, submission_repository: IFormSubmissionRepository):
        self.submission_repository = submission_repository
    
    async def handle(self, request: GetSubmissionsByAdminRequest) -> GetSubmissionsByAdminResponse:
        submissions = await self.submission_repository.get_by_admin_id(
            request.admin_id,
            request.skip,
            request.limit,
            request.date_from,
            request.date_to,
            request.user_name,
            request.user_email,
            request.field_value_search,
            request.form_id
        )
        return GetSubmissionsByAdminResponse(submissions=submissions)

