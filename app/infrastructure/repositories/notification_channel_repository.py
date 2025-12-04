"""SQLAlchemy implementation of NotificationChannelRepository"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import NotificationChannel, NotificationChannelType
from app.domain.repositories.notification_channel_repository import INotificationChannelRepository


class NotificationChannelRepository(INotificationChannelRepository):
    """SQLAlchemy implementation of notification channel repository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, channel_id: UUID) -> Optional[NotificationChannel]:
        """Get channel by ID"""
        result = await self.session.execute(
            select(NotificationChannel).where(NotificationChannel.id == channel_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_user_and_type(
        self, 
        user_id: UUID, 
        channel_type: NotificationChannelType
    ) -> Optional[NotificationChannel]:
        """Get user's channel by type"""
        result = await self.session.execute(
            select(NotificationChannel).where(
                NotificationChannel.user_id == user_id,
                NotificationChannel.channel_type == channel_type
            )
        )
        return result.scalar_one_or_none()
    
    async def get_enabled_channels_by_user(
        self, 
        user_id: UUID, 
        channel_type: Optional[NotificationChannelType] = None
    ) -> List[NotificationChannel]:
        """Get all enabled channels for a user, optionally filtered by type"""
        query = select(NotificationChannel).where(
            NotificationChannel.user_id == user_id,
            NotificationChannel.is_enabled == True
        )
        
        if channel_type:
            query = query.where(NotificationChannel.channel_type == channel_type)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def create(self, channel: NotificationChannel) -> NotificationChannel:
        """Create a new notification channel"""
        self.session.add(channel)
        await self.session.flush()
        await self.session.refresh(channel)
        return channel
    
    async def update(self, channel: NotificationChannel) -> NotificationChannel:
        """Update an existing notification channel"""
        await self.session.flush()
        await self.session.refresh(channel)
        return channel
    
    async def delete(self, channel_id: UUID) -> bool:
        """Delete a notification channel"""
        channel = await self.get_by_id(channel_id)
        if not channel:
            return False
        
        await self.session.delete(channel)
        await self.session.flush()
        return True
