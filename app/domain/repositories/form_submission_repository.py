from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.domain.models import FormSubmission


class IFormSubmissionRepository(ABC):
    @abstractmethod
    async def create(self, submission: FormSubmission) -> FormSubmission:
        pass
    
    @abstractmethod
    async def get_by_id(self, submission_id: UUID) -> Optional[FormSubmission]:
        pass
    
    @abstractmethod
    async def get_by_form_id(self, form_id: UUID, skip: int = 0, limit: int = 10) -> List[FormSubmission]:
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: UUID, skip: int = 0, limit: int = 10) -> List[FormSubmission]:
        pass
    
    @abstractmethod
    async def get_by_admin_id(
        self, 
        admin_id: UUID, 
        skip: int = 0, 
        limit: int = 10,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        user_name: Optional[str] = None,
        user_email: Optional[str] = None,
        field_value_search: Optional[str] = None,
        form_id: Optional[UUID] = None
    ) -> List[FormSubmission]:
        pass
    
    @abstractmethod
    async def count_by_form_id(self, form_id: UUID) -> int:
        pass
    
    @abstractmethod
    async def delete(self, submission_id: UUID) -> bool:
        pass

