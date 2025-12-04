from abc import ABC, abstractmethod
from uuid import UUID
from app.domain.models import Form


class IFormRepository(ABC):
    @abstractmethod
    async def create(self, form: Form) -> Form:
        pass
    
    @abstractmethod
    async def get_by_id(self, form_id: UUID) -> Form | None:
        pass
    
    @abstractmethod
    async def get_by_creator_id(self, creator_id: UUID, skip: int = 0, limit: int = 10) -> list[Form]:
        pass
    
    @abstractmethod
    async def update(self, form: Form) -> Form:
        pass
    
    @abstractmethod
    async def delete(self, form_id: UUID) -> bool:
        pass

