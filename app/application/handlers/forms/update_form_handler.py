from uuid import UUID
from typing import Any
from datetime import datetime
from pydantic import BaseModel
from mediatr import GenericQuery, Mediator
from dependency_injector.wiring import inject, Provide

from app.application.ports.usecase import UseCase
from app.domain.models import Form, FormField
from app.domain.repositories.form_repository import IFormRepository
from app.application.dto.models import FormDTO, FormFieldDTO
from typing import TYPE_CHECKING
from app.core.container import Container  # noqa: F401


class UpdateFormResponse(BaseModel):
    """Response containing updated form."""
    form: FormDTO


class UpdateFormRequest(BaseModel, GenericQuery[UpdateFormResponse]):
    """Request for updating a form."""
    form_id: UUID
    title: str | None = None
    description: str | None = None
    fields: list[dict[str, Any]] | None = None


@Mediator.handler
class UpdateFormHandler(UseCase[UpdateFormRequest, UpdateFormResponse]):
    """Use case for updating a form."""
    
    @inject
    def __init__(self, form_repository: IFormRepository = Provide[Container.form_repository]):
        self.form_repository = form_repository
    
    async def handle(self, request: UpdateFormRequest) -> UpdateFormResponse:
        form = await self.form_repository.get_by_id(request.form_id)
        if not form:
            raise ValueError("Form not found")
        
        # Update basic fields
        if request.title is not None:
            form.title = request.title
        if request.description is not None:
            form.description = request.description
        
        form.updated_at = datetime.utcnow()
        
        # Update fields if provided
        if request.fields is not None:
            # Clear existing fields - need to delete them explicitly
            existing_fields = list(form.fields)
            for field in existing_fields:
                form.fields.remove(field)
            
            # Add new fields
            for idx, field_data in enumerate(request.fields):
                field = FormField(
                    form_id=form.id,
                    field_type=field_data["field_type"],
                    label=field_data["label"],
                    name=field_data["name"],
                    is_required=field_data.get("is_required", False),
                    order=field_data.get("order", idx),
                    options=field_data.get("options"),
                    placeholder=field_data.get("placeholder")
                )
                form.fields.append(field)
        
        updated_form = await self.form_repository.update(form)
        form_dto = FormDTO(
            id=updated_form.id,
            title=updated_form.title,
            description=updated_form.description,
            creator_id=updated_form.creator_id,
            created_at=updated_form.created_at,
            updated_at=updated_form.updated_at,
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
                ) for f in updated_form.fields
            ]
        )
        return UpdateFormResponse(form=form_dto)

