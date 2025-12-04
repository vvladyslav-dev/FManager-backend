"""Repository interface for NotificationChannel"""
from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from app.domain.models import NotificationChannel, NotificationChannelType


class INotificationChannelRepository(ABC):
    """Interface for notification channel repository"""
    
    @abstractmethod
    async def get_by_id(self, channel_id: UUID) -> Optional[NotificationChannel]:
        """Get channel by ID"""
        pass
    
    @abstractmethod
    async def get_by_user_and_type(
        self, 
        user_id: UUID, 
        channel_type: NotificationChannelType
    ) -> Optional[NotificationChannel]:
        """Get user's channel by type"""
        pass
    
    @abstractmethod
    async def get_enabled_channels_by_user(
        self, 
        user_id: UUID, 
        channel_type: Optional[NotificationChannelType] = None
    ) -> List[NotificationChannel]:
        """Get all enabled channels for a user, optionally filtered by type"""
        pass
    
    @abstractmethod
    async def create(self, channel: NotificationChannel) -> NotificationChannel:
        """Create a new notification channel"""
        pass
    
    @abstractmethod
    async def update(self, channel: NotificationChannel) -> NotificationChannel:
        """Update an existing notification channel"""
        pass
    
    @abstractmethod
    async def delete(self, channel_id: UUID) -> bool:
        """Delete a notification channel"""
        pass
