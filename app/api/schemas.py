from uuid import UUID
from typing import Any, Optional, Dict
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
    options: str | None = None
    placeholder: str | None = None
    
    class Config:
        from_attributes = True


class FormSchema(BaseModel):
    id: UUID
    title: str
    description: str | None = None
    creator_id: UUID
    created_at: datetime
    fields: list[FormFieldSchema] = []
    
    class Config:
        from_attributes = True


class CreateFormRequest(BaseModel):
    title: str
    description: str | None = None
    fields: list[dict[str, Any]]


class UpdateFormRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    fields: list[dict[str, Any]] | None = None


# Form Submission schemas
class FormFieldValueSchema(BaseModel):
    id: UUID
    field_id: UUID
    value: str | None = None
    
    class Config:
        from_attributes = True


class FileSchema(BaseModel):
    id: UUID
    field_id: UUID | None = None
    original_filename: str
    blob_url: str
    file_size: int
    content_type: str | None = None
    
    class Config:
        from_attributes = True


class UserSchema(BaseModel):
    id: UUID
    name: str
    email: str | None = None
    is_admin: bool
    is_super_admin: bool = False
    is_approved: bool = True
    admin_id: UUID | None = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class CreateUserRequest(BaseModel):
    name: str
    email: str | None = None
    is_admin: bool = False
    admin_id: UUID | None = None


class UpdateUserRequest(BaseModel):
    name: str | None = None
    email: str | None = None
    is_admin: bool | None = None


class FormSubmissionSchema(BaseModel):
    id: UUID
    form_id: UUID
    user_id: UUID
    submitted_at: datetime
    user: UserSchema | None = None
    form: FormSchema | None = None
    field_values: list[FormFieldValueSchema] = []
    files: list[FileSchema] = []
    
    class Config:
        from_attributes = True


class SubmitFormRequest(BaseModel):
    user_name: str
    user_email: str | None = None
    field_values: dict[str, Any]  # field_id -> value
    files: dict[str, Any] | None = None  # field_id -> file data


# Auth schemas
class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    is_admin: bool = False


class LoginRequest(BaseModel):
    email: str
    password: str


# Notification settings schemas
class NotificationSettingsUpdate(BaseModel):
    """Schema for updating notification settings"""
    telegram_chat_id: Optional[str] = None
    telegram_notifications_enabled: Optional[bool] = None
    email_notifications_enabled: Optional[bool] = None
    notification_preferences: Optional[Dict[str, Any]] = None


class NotificationSettingsResponse(BaseModel):
    """Schema for notification settings response"""
    telegram_chat_id: Optional[str]
    telegram_notifications_enabled: bool
    email_notifications_enabled: bool
    notification_preferences: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True

