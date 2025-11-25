from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from app.domain.models import Form
from app.domain.repositories.form_repository import IFormRepository


class FormRepository(IFormRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, form: Form) -> Form:
        self.session.add(form)
        await self.session.commit()
        # Reload form with fields to avoid lazy loading issues
        form_id = form.id
        result = await self.session.execute(
            select(Form)
            .options(selectinload(Form.fields))
            .where(Form.id == form_id)
        )
        return result.scalar_one()
    
    async def get_by_id(self, form_id):
        result = await self.session.execute(
            select(Form)
            .options(selectinload(Form.fields))
            .where(Form.id == form_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_creator_id(self, creator_id, skip: int = 0, limit: int = 10):
        result = await self.session.execute(
            select(Form)
            .options(selectinload(Form.fields))
            .where(Form.creator_id == creator_id)
            .order_by(Form.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def update(self, form: Form) -> Form:
        await self.session.commit()
        await self.session.refresh(form)
        form_id = form.id
        result = await self.session.execute(
            select(Form)
            .options(selectinload(Form.fields))
            .where(Form.id == form_id)
        )
        return result.scalar_one()
    
    async def delete(self, form_id: UUID) -> bool:
        form = await self.get_by_id(form_id)
        if not form:
            return False
        await self.session.delete(form)
        await self.session.commit()
        return True

