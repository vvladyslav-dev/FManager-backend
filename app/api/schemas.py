from uuid import UUID
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


# Form schemas
class FormFieldSchema(BaseModel):
    id: UUID
    field_type: str
    label: str
    name: str
    is_required: bool
    order: int
    options: Optional[str] = None
    placeholder: Optional[str] = None
    
    class Config:
        from_attributes = True


class FormSchema(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    creator_id: UUID
    created_at: datetime
    fields: List[FormFieldSchema] = []
    
    class Config:
        from_attributes = True


class CreateFormRequest(BaseModel):
    title: str
    description: Optional[str] = None
    fields: List[Dict[str, Any]]


class UpdateFormRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    fields: Optional[List[Dict[str, Any]]] = None


# Form Submission schemas
class FormFieldValueSchema(BaseModel):
    id: UUID
    field_id: UUID
    value: Optional[str] = None
    
    class Config:
        from_attributes = True


class FileSchema(BaseModel):
    id: UUID
    field_id: Optional[UUID] = None
    original_filename: str
    blob_url: str
    file_size: int
    content_type: Optional[str] = None
    
    class Config:
        from_attributes = True


class UserSchema(BaseModel):
    id: UUID
    name: str
    email: Optional[str] = None
    is_admin: bool
    is_super_admin: bool = False
    is_approved: bool = True
    admin_id: Optional[UUID] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class CreateUserRequest(BaseModel):
    name: str
    email: Optional[str] = None
    is_admin: bool = False
    admin_id: Optional[UUID] = None


class UpdateUserRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    is_admin: Optional[bool] = None


class FormSubmissionSchema(BaseModel):
    id: UUID
    form_id: UUID
    user_id: UUID
    submitted_at: datetime
    user: Optional[UserSchema] = None
    form: Optional[FormSchema] = None
    field_values: List[FormFieldValueSchema] = []
    files: List[FileSchema] = []
    
    class Config:
        from_attributes = True


class SubmitFormRequest(BaseModel):
    user_name: str
    user_email: Optional[str] = None
    field_values: Dict[str, Any]  # field_id -> value
    files: Optional[Dict[str, Any]] = None  # field_id -> file data


# Auth schemas
class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    is_admin: bool = False


class LoginRequest(BaseModel):
    email: str
    password: str

