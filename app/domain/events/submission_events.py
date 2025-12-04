from dataclasses import dataclass
from uuid import UUID
from app.domain.events.base_event import DomainEvent


@dataclass
class SubmissionCreatedEvent(DomainEvent):
    """Event raised when a new form submission is created."""
    submission_id: UUID
    form_id: UUID
    user_id: UUID
    
    def __init__(self, submission_id: UUID, form_id: UUID, user_id: UUID):
        super().__init__()
        self.submission_id = submission_id
        self.form_id = form_id
        self.user_id = user_id
