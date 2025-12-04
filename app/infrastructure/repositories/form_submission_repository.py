from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import datetime
from uuid import UUID
from app.domain.models import FormSubmission, Form, User, FormFieldValue
from app.domain.repositories.form_submission_repository import IFormSubmissionRepository


class FormSubmissionRepository(IFormSubmissionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, submission: FormSubmission) -> FormSubmission:
        self.session.add(submission)
        await self.session.flush()
        # Reload submission with all related objects to avoid lazy loading issues
        submission_id = submission.id
        result = await self.session.execute(
            select(FormSubmission)
            .options(
                selectinload(FormSubmission.form).selectinload(Form.fields),
                selectinload(FormSubmission.user),
                selectinload(FormSubmission.field_values),
                selectinload(FormSubmission.files)
            )
            .where(FormSubmission.id == submission_id)
        )
        return result.scalar_one()
    
    async def get_by_id(self, submission_id):
        result = await self.session.execute(
            select(FormSubmission)
            .options(
                selectinload(FormSubmission.form).selectinload(Form.fields),
                selectinload(FormSubmission.user),
                selectinload(FormSubmission.field_values),
                selectinload(FormSubmission.files)
            )
            .where(FormSubmission.id == submission_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_form_id(self, form_id, skip: int = 0, limit: int = 10):
        result = await self.session.execute(
            select(FormSubmission)
            .options(
                selectinload(FormSubmission.user),
                selectinload(FormSubmission.field_values),
                selectinload(FormSubmission.files)
            )
            .where(FormSubmission.form_id == form_id)
            .order_by(FormSubmission.submitted_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_user_id(self, user_id, skip: int = 0, limit: int = 10):
        result = await self.session.execute(
            select(FormSubmission)
            .options(
                selectinload(FormSubmission.form).selectinload(Form.fields),
                selectinload(FormSubmission.field_values),
                selectinload(FormSubmission.files)
            )
            .where(FormSubmission.user_id == user_id)
            .order_by(FormSubmission.submitted_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_admin_id(
        self, 
        admin_id, 
        skip: int = 0, 
        limit: int = 10,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        user_name: str | None = None,
        user_email: str | None = None,
        field_value_search: str | None = None,
        form_id: UUID | None = None
    ):
        # Get submissions for forms created by admin and users created by admin
        query = (
            select(FormSubmission)
            .join(Form, FormSubmission.form_id == Form.id)
            .join(User, FormSubmission.user_id == User.id)
            .options(
                selectinload(FormSubmission.form).selectinload(Form.fields),
                selectinload(FormSubmission.user),
                selectinload(FormSubmission.field_values),
                selectinload(FormSubmission.files)
            )
            .where(
                (Form.creator_id == admin_id) | (User.admin_id == admin_id)
            )
        )
        
        # Apply form_id filter
        if form_id:
            query = query.where(FormSubmission.form_id == form_id)
        
        # Apply date filters
        if date_from:
            query = query.where(FormSubmission.submitted_at >= date_from)
        if date_to:
            query = query.where(FormSubmission.submitted_at <= date_to)
        
        # Apply user name filter
        if user_name:
            query = query.where(User.name.ilike(f"%{user_name}%"))
        
        # Apply user email filter
        if user_email:
            query = query.where(User.email.ilike(f"%{user_email}%"))
        
        # Apply field value search filter
        if field_value_search:
            # Join with FormFieldValue to search in field values
            query = query.join(
                FormFieldValue,
                FormSubmission.id == FormFieldValue.submission_id
            ).where(
                FormFieldValue.value.ilike(f"%{field_value_search}%")
            ).distinct()
        
        query = query.order_by(FormSubmission.submitted_at.desc()).offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def count_by_form_id(self, form_id: UUID) -> int:
        """Count submissions for a specific form."""
        result = await self.session.execute(
            select(func.count(FormSubmission.id))
            .where(FormSubmission.form_id == form_id)
        )
        return result.scalar_one() or 0
    
    async def delete(self, submission_id: UUID) -> bool:
        """Delete a submission by ID."""
        submission = await self.get_by_id(submission_id)
        if not submission:
            return False
        await self.session.delete(submission)
        await self.session.flush()
        return True

