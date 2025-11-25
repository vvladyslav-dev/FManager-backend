from dataclasses import dataclass
from uuid import UUID
from typing import Optional
from mediatr import GenericQuery

from app.application.ports.usecase import UseCase
from app.domain.models import Form
from app.domain.repositories.form_repository import IFormRepository


@dataclass
class GetFormResponse:
    """Response containing form."""
    form: Optional[Form]


@dataclass
class GetFormRequest(GenericQuery[GetFormResponse]):
    """Request for getting a form by ID."""
    form_id: UUID


class GetFormHandler(UseCase[GetFormRequest, GetFormResponse]):
    """Use case for getting a form by ID."""
    
    def __init__(self, form_repository: IFormRepository):
        self.form_repository = form_repository
    
    async def handle(self, request: GetFormRequest) -> GetFormResponse:
        form = await self.form_repository.get_by_id(request.form_id)
        return GetFormResponse(form=form)

