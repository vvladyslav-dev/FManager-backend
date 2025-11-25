from dataclasses import dataclass, field
from uuid import UUID
from typing import List, Optional, Dict, Any
from datetime import datetime
from mediatr import GenericQuery

from app.application.ports.usecase import UseCase
from app.domain.models import Form, FormField
from app.domain.repositories.form_repository import IFormRepository


@dataclass
class UpdateFormResponse:
    """Response containing updated form."""
    form: Form


@dataclass
class UpdateFormRequest(GenericQuery[UpdateFormResponse]):
    """Request for updating a form."""
    form_id: UUID
    title: Optional[str] = None
    description: Optional[str] = None
    fields: Optional[List[Dict[str, Any]]] = None


class UpdateFormHandler(UseCase[UpdateFormRequest, UpdateFormResponse]):
    """Use case for updating a form."""
    
    def __init__(self, form_repository: IFormRepository):
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
            # Clear existing fields
            form.fields.clear()
            
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
        return UpdateFormResponse(form=updated_form)

