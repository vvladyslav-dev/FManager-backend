import logging
from app.domain.events.submission_events import SubmissionCreatedEvent
from app.domain.services.notification_service import INotificationService
from app.domain.repositories.user_repository import IUserRepository
from app.domain.repositories.form_repository import IFormRepository
from app.domain.repositories.form_submission_repository import IFormSubmissionRepository
from app.domain.repositories.notification_channel_repository import INotificationChannelRepository
from app.domain.models import NotificationChannelType
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.form_repository import FormRepository
from app.infrastructure.repositories.form_submission_repository import FormSubmissionRepository
from app.infrastructure.repositories.notification_channel_repository import NotificationChannelRepository


logger = logging.getLogger(__name__)


class TelegramNotificationHandler:
    """Event handler for sending Telegram notifications on submission creation."""
    
    def __init__(
        self,
        notification_service: INotificationService,
    ):
        """
        Initialize handler.
        
        Args:
            notification_service: Telegram notification service instance
            user_repository: User repository for fetching user data
            form_repository: Form repository for fetching form data
            submission_repository: Submission repository for fetching submission data
            notification_channel_repository: Notification channel repository
        """
        self.notification_service = notification_service
    
    async def handle(self, event: SubmissionCreatedEvent) -> None:
        """
        Handle SubmissionCreatedEvent by sending Telegram notification.
        
        Args:
            event: The submission created event
        """
        # Use a fresh DB session for handling the event (read-only operations)
        async with AsyncSessionLocal() as session:
            submission_repo: IFormSubmissionRepository = FormSubmissionRepository(session)
            form_repo: IFormRepository = FormRepository(session)
            user_repo: IUserRepository = UserRepository(session)
            channel_repo: INotificationChannelRepository = NotificationChannelRepository(session)

            # Fetch full submission data with relationships
            submission = await submission_repo.get_by_id(event.submission_id)
        
            if not submission:
                logger.warning(f"Submission {event.submission_id} not found")
                return
            
            # Get form
            form = await form_repo.get_by_id(event.form_id)
            if not form:
                logger.warning(f"Form {event.form_id} not found")
                return
            
            # Get form creator (admin who owns the form)
            admin = await user_repo.get_by_id(form.creator_id)
            if not admin:
                logger.warning(f"Admin {form.creator_id} not found")
                return
            
            # Get admin's Telegram notification channel
            channel = await channel_repo.get_by_user_and_type(
                user_id=admin.id,
                channel_type=NotificationChannelType.TELEGRAM
            )
            
            logger.info(f"Channel found: {channel is not None}, is_enabled: {channel.is_enabled if channel else 'N/A'}")
            
            if not channel or not channel.is_enabled:
                logger.info(
                    f"Telegram notifications disabled or not configured for admin {admin.id}"
                )
                return
            
            # Extract chat_id from config
            chat_id = channel.config.get('chat_id')
            if not chat_id:
                logger.warning(f"No chat_id in Telegram channel config for admin {admin.id}")
                return
            
            logger.info(f"Sending notification to chat_id: {chat_id}")
            
            # Get user who submitted
            user = await user_repo.get_by_id(event.user_id)
            
            # Prepare field values for the message
            field_values = []
            if submission.field_values:
                for field_value in submission.field_values:
                    # Find the field definition
                    field = next((f for f in form.fields if f.id == field_value.field_id), None)
                    if field:
                        field_values.append({
                            'label': field.label,
                            'value': field_value.value,
                            'type': field.field_type
                        })
            
            # Add file fields info
            if submission.files:
                # Group files by field_id
                files_by_field = {}
                for file in submission.files:
                    if file.field_id not in files_by_field:
                        files_by_field[file.field_id] = []
                    files_by_field[file.field_id].append(file)
                
                # Add to field_values
                for field_id, files in files_by_field.items():
                    field = next((f for f in form.fields if f.id == field_id), None)
                    if field:
                        field_values.append({
                            'label': field.label,
                            'value': '',
                            'type': 'file',
                            'file_count': len(files)
                        })
        
        # Format message (outside session - no DB access needed)
        message = await self.notification_service.format_submission_message(
            form_title=form.title,
            user_name=user.name if user else "Unknown User",
            user_email=user.email if user and user.email else None,
            submitted_at=submission.submitted_at.strftime("%Y-%m-%d %H:%M:%S"),
            field_values=field_values
        )
        
        # Send notification
        success = await self.notification_service.send_notification(
            chat_id=chat_id,
            message=message
        )
        
        if success:
            logger.info(
                f"Telegram notification sent to admin {admin.id} for submission {submission.id}"
            )
        else:
            logger.error(
                f"Failed to send Telegram notification to admin {admin.id} for submission {submission.id}"
            )
