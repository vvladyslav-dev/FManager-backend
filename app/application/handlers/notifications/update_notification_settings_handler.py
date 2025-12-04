"""Handler for updating user notification settings"""
from pydantic import BaseModel
from mediatr import GenericQuery, Mediator
from dependency_injector.wiring import inject, Provide
from app.core.container import Container  # noqa: F401
from uuid import UUID, uuid4
from typing import Optional

from app.domain.repositories.user_repository import IUserRepository
from app.domain.repositories.notification_channel_repository import INotificationChannelRepository
from app.domain.models import NotificationChannel, NotificationChannelType
from app.domain.services.notification_config_validator import NotificationConfigValidator
from app.application.ports.usecase import UseCase



class UpdateNotificationSettingsResponse(BaseModel):
    telegram_chat_id: Optional[str]
    telegram_notifications_enabled: bool
    email_notifications_enabled: bool
    notification_preferences: Optional[dict] = None


class UpdateNotificationSettingsRequest(BaseModel, GenericQuery[UpdateNotificationSettingsResponse]):
    user_id: UUID
    telegram_chat_id: Optional[str] = None
    telegram_notifications_enabled: Optional[bool] = None
    email_notifications_enabled: Optional[bool] = None


@Mediator.handler
class UpdateNotificationSettingsHandler(UseCase[UpdateNotificationSettingsRequest, UpdateNotificationSettingsResponse]):
    """Use case handler for updating notification settings"""
    
    @inject
    def __init__(
        self,
        user_repository: IUserRepository = Provide[Container.user_repository],
        notification_channel_repository: INotificationChannelRepository = Provide[Container.notification_channel_repository]
    ):
        self.user_repository = user_repository
        self.notification_channel_repository = notification_channel_repository
    
    async def handle(self, request: UpdateNotificationSettingsRequest) -> UpdateNotificationSettingsResponse:
        """
        Update notification settings for a user.
        
        Args:
            request: Request containing user_id and notification settings
            
        Returns:
            Response with updated notification settings
            
        Raises:
            ValueError: If user not found or validation fails
        """
        # Verify user exists
        user = await self.user_repository.get_by_id(request.user_id)
        if not user:
            raise ValueError(f"User {request.user_id} not found")
        
        # Get existing Telegram channel
        telegram_channel = await self.notification_channel_repository.get_by_user_and_type(
            user_id=request.user_id,
            channel_type=NotificationChannelType.TELEGRAM
        )
        
        # Update or create Telegram channel
        if request.telegram_chat_id is not None or request.telegram_notifications_enabled is not None:
            if telegram_channel:
                # Update existing
                if request.telegram_chat_id is not None:
                    config = {"chat_id": request.telegram_chat_id}
                    NotificationConfigValidator.validate(NotificationChannelType.TELEGRAM, config)
                    telegram_channel.config = config
                
                if request.telegram_notifications_enabled is not None:
                    telegram_channel.is_enabled = request.telegram_notifications_enabled
                
                await self.notification_channel_repository.update(telegram_channel)
            
            elif request.telegram_chat_id:
                # Create new
                config = {"chat_id": request.telegram_chat_id}
                NotificationConfigValidator.validate(NotificationChannelType.TELEGRAM, config)
                
                telegram_channel = NotificationChannel(
                    id=uuid4(),
                    user_id=request.user_id,
                    channel_type=NotificationChannelType.TELEGRAM,
                    is_enabled=request.telegram_notifications_enabled if request.telegram_notifications_enabled is not None else False,
                    config=config
                )
                await self.notification_channel_repository.create(telegram_channel)
        
        # Get updated settings
        telegram_channel = await self.notification_channel_repository.get_by_user_and_type(
            user_id=request.user_id,
            channel_type=NotificationChannelType.TELEGRAM
        )
        
        telegram_chat_id = None
        telegram_notifications_enabled = False
        if telegram_channel:
            telegram_chat_id = telegram_channel.config.get('chat_id')
            telegram_notifications_enabled = telegram_channel.is_enabled
        
        return UpdateNotificationSettingsResponse(
            telegram_chat_id=telegram_chat_id,
            telegram_notifications_enabled=telegram_notifications_enabled,
            email_notifications_enabled=False,
            notification_preferences=None
        )
