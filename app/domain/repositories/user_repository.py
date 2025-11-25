from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from app.domain.models import User


class IUserRepository(ABC):
    @abstractmethod
    async def create(self, user: User) -> User:
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass
    
    @abstractmethod
    async def get_by_admin_id(self, admin_id: UUID) -> List[User]:
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        pass
    
    @abstractmethod
    async def get_unapproved_admins(self) -> List[User]:
        """Get all admin users that are not approved yet."""
        pass

