from uuid import UUID, uuid4
from typing import Any
from pydantic import BaseModel
from mediatr import GenericQuery, Mediator
from dependency_injector.wiring import inject, Provide
from app.core.container import Container  # noqa: F401

from app.application.ports.usecase import UseCase
from app.domain.models import Form, FormField
from app.domain.repositories.form_repository import IFormRepository
from app.application.dto.models import FormDTO, FormFieldDTO
from typing import TYPE_CHECKING


class CreateFormResponse(BaseModel):
    """Response containing created form."""
    form: FormDTO


class CreateFormRequest(BaseModel, GenericQuery[CreateFormResponse]):
    """Request for creating a new form."""
    title: str
    creator_id: UUID | None = None
    description: str | None = None
    fields: list[dict[str, Any]] = []


@Mediator.handler
class CreateFormHandler(UseCase[CreateFormRequest, CreateFormResponse]):
    """Use case for creating a new form."""
    
    @inject
    def __init__(self, form_repository: IFormRepository = Provide[Container.form_repository]):
        self.form_repository = form_repository
    
    async def handle(self, request: CreateFormRequest) -> CreateFormResponse:
        form = Form(
            id=uuid4(),
            title=request.title,
            description=request.description,
            creator_id=request.creator_id
        )

        # Create form fields
        if request.fields:
            for idx, field_data in enumerate(request.fields):
                field = FormField(
                    id=uuid4(),
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
        
        created_form = await self.form_repository.create(form)
        
        form_dto = FormDTO(
            id=created_form.id,
            title=created_form.title,
            description=created_form.description,
            creator_id=created_form.creator_id,
            created_at=created_form.created_at,
            updated_at=created_form.updated_at,
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
                ) for f in created_form.fields
            ]
        )
        return CreateFormResponse(form=form_dto)

