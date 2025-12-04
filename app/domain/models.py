from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Integer, JSON, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from enum import Enum

from app.core.database import Base


class NotificationChannelType(str, Enum):
    """Supported notification channel types"""
    TELEGRAM = "telegram"


class NotificationChannel(Base):
    """
    Notification channels table.
    Supports Telegram notifications.
    
    Config structure:
    - telegram: {"chat_id": str}
    """
    __tablename__ = "notification_channels"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    channel_type = Column(SQLEnum(NotificationChannelType), nullable=False)
    is_enabled = Column(Boolean, default=False, nullable=False)
    config = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="notification_channels")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'channel_type', name='uq_user_channel_type'),
    )
    
    def __repr__(self):
        return f"<NotificationChannel(user_id={self.user_id}, type={self.channel_type.value}, enabled={self.is_enabled})>"


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=True, index=True)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=True)  # For admin users with authentication
    avatar_url = Column(String(1000), nullable=True)
    is_admin = Column(Boolean, default=False, nullable=False)
    is_super_admin = Column(Boolean, default=False, nullable=False)
    is_approved = Column(Boolean, default=True, nullable=False)  # For admins: False until approved by super admin
    admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    created_forms = relationship("Form", back_populates="creator", foreign_keys="Form.creator_id")
    submissions = relationship("FormSubmission", back_populates="user")
    admin_users = relationship("User", remote_side=[id], foreign_keys=[admin_id])
    notification_channels = relationship("NotificationChannel", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, is_admin={self.is_admin})>"


class Form(Base):
    __tablename__ = "forms"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    creator = relationship("User", back_populates="created_forms", foreign_keys=[creator_id])
    fields = relationship("FormField", back_populates="form", cascade="all, delete-orphan", order_by="FormField.order")
    submissions = relationship("FormSubmission", back_populates="form", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Form(id={self.id}, title={self.title})>"


class FormField(Base):
    __tablename__ = "form_fields"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    form_id = Column(UUID(as_uuid=True), ForeignKey("forms.id"), nullable=False)
    field_type = Column(String(50), nullable=False)  # text, textarea, file, number, etc.
    label = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    is_required = Column(Boolean, default=False, nullable=False)
    order = Column(Integer, nullable=False)
    options = Column(Text, nullable=True)  # JSON string for select/radio options
    placeholder = Column(String(255), nullable=True)  # Optional placeholder text
    
    # Relationships
    form = relationship("Form", back_populates="fields")
    values = relationship("FormFieldValue", back_populates="field", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<FormField(id={self.id}, name={self.name}, type={self.field_type})>"


class FormSubmission(Base):
    __tablename__ = "form_submissions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    form_id = Column(UUID(as_uuid=True), ForeignKey("forms.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    form = relationship("Form", back_populates="submissions")
    user = relationship("User", back_populates="submissions")
    field_values = relationship("FormFieldValue", back_populates="submission", cascade="all, delete-orphan")
    files = relationship("File", back_populates="submission", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<FormSubmission(id={self.id}, form_id={self.form_id}, user_id={self.user_id})>"


class FormFieldValue(Base):
    __tablename__ = "form_field_values"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("form_submissions.id"), nullable=False)
    field_id = Column(UUID(as_uuid=True), ForeignKey("form_fields.id"), nullable=False)
    value = Column(Text, nullable=True)
    
    # Relationships
    submission = relationship("FormSubmission", back_populates="field_values")
    field = relationship("FormField", back_populates="values")
    
    def __repr__(self):
        return f"<FormFieldValue(id={self.id}, field_id={self.field_id})>"


class File(Base):
    __tablename__ = "files"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("form_submissions.id"), nullable=False)
    field_id = Column(UUID(as_uuid=True), ForeignKey("form_fields.id"), nullable=True)
    original_filename = Column(String(255), nullable=False)
    blob_name = Column(String(500), nullable=False)  # Azure blob name
    blob_url = Column(String(1000), nullable=False)  # Azure blob URL
    file_size = Column(Integer, nullable=False)  # Size in bytes
    content_type = Column(String(100), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    submission = relationship("FormSubmission", back_populates="files")
    
    def __repr__(self):
        return f"<File(id={self.id}, filename={self.original_filename})>"

