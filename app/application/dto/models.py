from __future__ import annotations
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class FormFieldDTO(BaseModel):
    id: Optional[UUID] = None
    field_type: str
    label: str
    name: str
    is_required: bool
    order: int
    options: Optional[str] = None
    placeholder: Optional[str] = None


class FormDTO(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    creator_id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    fields: List[FormFieldDTO] = []


class UserDTO(BaseModel):
    id: UUID
    name: str
    email: Optional[str] = None
    is_admin: bool
    is_super_admin: bool = False
    is_approved: bool = True
    admin_id: Optional[UUID] = None
    avatar_url: Optional[str] = None
    created_at: Optional[datetime] = None


class FormFieldValueDTO(BaseModel):
    id: UUID
    field_id: UUID
    value: Optional[str] = None


class FileDTO(BaseModel):
    id: UUID
    field_id: Optional[UUID] = None
    original_filename: str
    blob_url: str
    file_size: int
    content_type: Optional[str] = None


class FormSubmissionDTO(BaseModel):
    id: UUID
    form_id: UUID
    user_id: UUID
    submitted_at: datetime
    user: Optional[UserDTO] = None
    form: Optional[FormDTO] = None
    field_values: List[FormFieldValueDTO] = []
    files: List[FileDTO] = []
