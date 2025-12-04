from abc import ABC, abstractmethod
from uuid import UUID
from app.domain.models import File


class IFileRepository(ABC):
    @abstractmethod
    async def create(self, file: File) -> File:
        pass
    
    @abstractmethod
    async def get_by_id(self, file_id: UUID) -> File | None:
        pass
    
    @abstractmethod
    async def get_by_submission_id(self, submission_id: UUID) -> list[File]:
        pass

