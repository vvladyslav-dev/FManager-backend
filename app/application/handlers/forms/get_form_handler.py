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


class GetFormResponse(BaseModel):
    """Response containing form."""
    form: FormDTO | None


class GetFormRequest(BaseModel, GenericQuery[GetFormResponse]):
    """Request for getting a form by ID."""
    form_id: UUID


@Mediator.handler
class GetFormHandler(UseCase[GetFormRequest, GetFormResponse]):
    """Use case for getting a form by ID."""
    
    @inject
    def __init__(self, form_repository: IFormRepository = Provide[Container.form_repository]):
        self.form_repository = form_repository
    
    async def handle(self, request: GetFormRequest) -> GetFormResponse:
        form = await self.form_repository.get_by_id(request.form_id)
        if not form:
            return GetFormResponse(form=None)
        form_dto = FormDTO(
            id=form.id,
            title=form.title,
            description=form.description,
            creator_id=form.creator_id,
            created_at=form.created_at,
            updated_at=form.updated_at,
            fields=[
                FormFieldDTO(
                    id=f.id,
                    field_type=f.field_type,
                    label=f.label,
                    name=f.name,
                    is_required=f.is_required,
                    order=f.order,
                    options=f.options,
                    placeholder=getattr(f, 'placeholder', None)
                ) for f in form.fields
            ]
        )
        return GetFormResponse(form=form_dto)

