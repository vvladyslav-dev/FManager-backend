from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.form_repository import FormRepository
from app.infrastructure.repositories.form_submission_repository import FormSubmissionRepository
from app.infrastructure.repositories.file_repository import FileRepository
from app.infrastructure.repositories.notification_channel_repository import NotificationChannelRepository
from app.infrastructure.services.submission_export_service import SubmissionExportService
from app.infrastructure.services.telegram_notification_service import TelegramNotificationService
from app.infrastructure.services.telegram_bot_polling_service import TelegramBotPollingService
from app.domain.events.event_bus import EventBus
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class Container(containers.DeclarativeContainer):
    """Dependency Injection Container"""
    
    # Database session provider - will be injected from FastAPI Depends
    db_session = providers.Dependency(instance_of=AsyncSession)
    
    # Repository providers
    user_repository = providers.Factory(
        UserRepository,
        session=db_session
    )
    
    form_repository = providers.Factory(
        FormRepository,
        session=db_session
    )
    
    form_submission_repository = providers.Factory(
        FormSubmissionRepository,
        session=db_session
    )
    
    file_repository = providers.Factory(
        FileRepository,
        session=db_session
    )
    
    notification_channel_repository = providers.Factory(
        NotificationChannelRepository,
        session=db_session
    )
    
    # Service providers
    submission_export_service = providers.Factory(
        SubmissionExportService
    )
    
    # Event Bus - Singleton
    event_bus = providers.Singleton(EventBus)
    
    # Notification Services
    telegram_notification_service = providers.Factory(
        TelegramNotificationService,
        bot_token=settings.telegram_bot_token
    )
    
    # Telegram Bot Polling Service - Singleton (one bot instance for entire app)
    telegram_bot_polling_service = providers.Singleton(
        TelegramBotPollingService,
        bot_token=settings.telegram_bot_token
    )
    
    # No handler providers here to avoid circular imports.

# Global container instance (for cases where session is provided via override)
container = Container()


