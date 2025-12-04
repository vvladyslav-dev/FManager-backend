"""Handler for getting user notification settings"""
from pydantic import BaseModel
from mediatr import GenericQuery, Mediator
from dependency_injector.wiring import inject, Provide
from app.core.container import Container  # noqa: F401
from uuid import UUID
from typing import Optional, TYPE_CHECKING

from app.domain.repositories.user_repository import IUserRepository
from app.domain.repositories.notification_channel_repository import INotificationChannelRepository
from app.domain.models import NotificationChannelType
from app.application.ports.usecase import UseCase

from typing import TYPE_CHECKING


class GetNotificationSettingsResponse(BaseModel):
    telegram_chat_id: Optional[str]
    telegram_notifications_enabled: bool
    email_notifications_enabled: bool
    notification_preferences: Optional[dict] = None


class GetNotificationSettingsRequest(BaseModel, GenericQuery[GetNotificationSettingsResponse]):
    user_id: UUID


@Mediator.handler
class GetNotificationSettingsHandler(UseCase[GetNotificationSettingsRequest, GetNotificationSettingsResponse]):
    """Use case handler for getting notification settings"""
    
    @inject
    def __init__(
        self,
        user_repository: IUserRepository = Provide[Container.user_repository],
        notification_channel_repository: INotificationChannelRepository = Provide[Container.notification_channel_repository]
    ):
        self.user_repository = user_repository
        self.notification_channel_repository = notification_channel_repository
    
    async def handle(self, request: GetNotificationSettingsRequest) -> GetNotificationSettingsResponse:
        """
        Get notification settings for a user.
        
        Args:
            request: Request containing user_id
            
        Returns:
            Response with notification settings
            
        Raises:
            ValueError: If user not found
        """
        # Verify user exists
        user = await self.user_repository.get_by_id(request.user_id)
        if not user:
            raise ValueError(f"User {request.user_id} not found")
        
        # Get Telegram channel
        telegram_channel = await self.notification_channel_repository.get_by_user_and_type(
            user_id=request.user_id,
            channel_type=NotificationChannelType.TELEGRAM
        )
        
        telegram_chat_id = None
        telegram_notifications_enabled = False
        if telegram_channel:
            telegram_chat_id = telegram_channel.config.get('chat_id')
            telegram_notifications_enabled = telegram_channel.is_enabled
        
        return GetNotificationSettingsResponse(
            telegram_chat_id=telegram_chat_id,
            telegram_notifications_enabled=telegram_notifications_enabled,
            email_notifications_enabled=False,
            notification_preferences=None
        )
