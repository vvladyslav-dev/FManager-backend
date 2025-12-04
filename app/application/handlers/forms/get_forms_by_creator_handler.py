from uuid import UUID
from pydantic import BaseModel
from mediatr import GenericQuery, Mediator
from dependency_injector.wiring import inject, Provide
from app.core.container import Container  # noqa: F401

from app.application.ports.usecase import UseCase
from app.domain.models import Form
from app.domain.repositories.form_repository import IFormRepository
from app.application.dto.models import FormDTO, FormFieldDTO
from typing import TYPE_CHECKING


class GetFormsByCreatorResponse(BaseModel):
    """Response containing forms created by creator."""
    forms: list[FormDTO]


class GetFormsByCreatorRequest(BaseModel, GenericQuery[GetFormsByCreatorResponse]):
    """Request for getting forms by creator ID."""
    creator_id: UUID
    skip: int = 0
    limit: int = 10


@Mediator.handler
class GetFormsByCreatorHandler(UseCase[GetFormsByCreatorRequest, GetFormsByCreatorResponse]):
    """Use case for getting forms by creator ID."""
    
    @inject
    def __init__(self, form_repository: IFormRepository = Provide[Container.form_repository]):
        self.form_repository = form_repository
    
    async def handle(self, request: GetFormsByCreatorRequest) -> GetFormsByCreatorResponse:
        forms = await self.form_repository.get_by_creator_id(request.creator_id, request.skip, request.limit)
        form_dtos = [
            FormDTO(
                id=f.id,
                title=f.title,
                description=f.description,
                creator_id=f.creator_id,
                created_at=f.created_at,
                updated_at=f.updated_at,
                fields=[
                    FormFieldDTO(
                        id=ff.id,
                        field_type=ff.field_type,
                        label=ff.label,
                        name=ff.name,
                        is_required=ff.is_required,
                        order=ff.order,
                        options=ff.options,
                        placeholder=getattr(ff, 'placeholder', None)
                    ) for ff in f.fields
                ]
            ) for f in forms
        ]
        return GetFormsByCreatorResponse(forms=form_dtos)

