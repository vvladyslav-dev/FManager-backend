from dataclasses import dataclass
from uuid import UUID
from typing import List
from mediatr import GenericQuery

from app.application.ports.usecase import UseCase
from app.domain.models import Form
from app.domain.repositories.form_repository import IFormRepository


@dataclass
class GetFormsByCreatorResponse:
    """Response containing forms created by creator."""
    forms: List[Form]


@dataclass
class GetFormsByCreatorRequest(GenericQuery[GetFormsByCreatorResponse]):
    """Request for getting forms by creator ID."""
    creator_id: UUID
    skip: int = 0
    limit: int = 10


class GetFormsByCreatorHandler(UseCase[GetFormsByCreatorRequest, GetFormsByCreatorResponse]):
    """Use case for getting forms by creator ID."""
    
    def __init__(self, form_repository: IFormRepository):
        self.form_repository = form_repository
    
    async def handle(self, request: GetFormsByCreatorRequest) -> GetFormsByCreatorResponse:
        forms = await self.form_repository.get_by_creator_id(request.creator_id, request.skip, request.limit)
        return GetFormsByCreatorResponse(forms=forms)

