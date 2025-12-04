from abc import ABC, abstractmethod
from uuid import UUID
from datetime import datetime
from app.domain.models import FormSubmission


class IFormSubmissionRepository(ABC):
    @abstractmethod
    async def create(self, submission: FormSubmission) -> FormSubmission:
        pass
    
    @abstractmethod
    async def get_by_id(self, submission_id: UUID) -> FormSubmission | None:
        pass
    
    @abstractmethod
    async def get_by_form_id(self, form_id: UUID, skip: int = 0, limit: int = 10) -> list[FormSubmission]:
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: UUID, skip: int = 0, limit: int = 10) -> list[FormSubmission]:
        pass
    
    @abstractmethod
    async def get_by_admin_id(
        self, 
        admin_id: UUID, 
        skip: int = 0, 
        limit: int = 10,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        user_name: str | None = None,
        user_email: str | None = None,
        field_value_search: str | None = None,
        form_id: UUID | None = None
    ) -> list[FormSubmission]:
        pass
    
    @abstractmethod
    async def count_by_form_id(self, form_id: UUID) -> int:
        pass
    
    @abstractmethod
    async def delete(self, submission_id: UUID) -> bool:
        pass

