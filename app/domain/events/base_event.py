from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class DomainEvent(ABC):
    """Base class for all domain events."""
    event_id: UUID
    occurred_at: datetime
    
    def __init__(self):
        self.event_id = uuid4()
        self.occurred_at = datetime.utcnow()
