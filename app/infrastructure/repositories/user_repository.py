from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from uuid import UUID
from app.domain.models import User
from app.domain.repositories.user_repository import IUserRepository


class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user
    
    async def get_by_id(self, user_id: UUID):
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str):
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_admin_id(self, admin_id: UUID):
        result = await self.session.execute(
            select(User).where(User.admin_id == admin_id)
        )
        return list(result.scalars().all())
    
    async def update(self, user: User) -> User:
        await self.session.flush()
        await self.session.refresh(user)
        return user
    
    async def delete(self, user_id: UUID) -> bool:
        result = await self.session.execute(
            delete(User).where(User.id == user_id)
        )
        await self.session.flush()
        return result.rowcount > 0
    
    async def get_unapproved_admins(self) -> list[User]:
        """Get all admin users that are not approved yet."""
        result = await self.session.execute(
            select(User).where(
                User.is_admin.is_(True),
                User.is_super_admin.is_(False),
                User.is_approved.is_(False)
            )
        )
        return list(result.scalars().all())

