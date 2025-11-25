from dataclasses import dataclass, field
from uuid import UUID, uuid4
from typing import List, Optional, Dict, Any
from mediatr import GenericQuery

from app.application.ports.usecase import UseCase
from app.domain.models import Form, FormField
from app.domain.repositories.form_repository import IFormRepository


@dataclass
class CreateFormResponse:
    """Response containing created form."""
    form: Form


@dataclass
class CreateFormRequest(GenericQuery[CreateFormResponse]):
    """Request for creating a new form."""
    title: str
    creator_id: UUID
    description: Optional[str] = None
    fields: List[Dict[str, Any]] = field(default_factory=list)


class CreateFormHandler(UseCase[CreateFormRequest, CreateFormResponse]):
    """Use case for creating a new form."""
    
    def __init__(self, form_repository: IFormRepository):
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
        
        return CreateFormResponse(form=created_form)

