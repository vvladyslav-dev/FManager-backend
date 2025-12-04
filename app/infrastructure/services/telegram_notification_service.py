import logging
from typing import Optional, List, Dict, Any
from uuid import UUID
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError

from app.domain.services.notification_service import INotificationService


logger = logging.getLogger(__name__)


class TelegramNotificationService(INotificationService):
    """Telegram implementation of notification service."""
    
    def __init__(self, bot_token: Optional[str] = None):
        """
        Initialize Telegram notification service.
        
        Args:
            bot_token: Telegram bot token from BotFather (optional)
        """
        self.bot = Bot(token=bot_token) if bot_token else None
        self.enabled = bot_token is not None
        
        if not self.enabled:
            logger.warning("Telegram bot token not configured. Notifications disabled.")
    
    async def send_notification(
        self,
        chat_id: str,
        message: str,
        parse_mode: Optional[str] = "HTML"
    ) -> bool:
        """
        Send notification via Telegram.
        
        Args:
            chat_id: Telegram chat ID
            message: Message content
            parse_mode: Message formatting mode
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled or not self.bot:
            logger.debug("Telegram notifications disabled, skipping")
            return False
        
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=parse_mode,
            )
            logger.info(f"Telegram notification sent successfully to chat_id: {chat_id}")
            return True
        except TelegramError as e:
            logger.error(f"Failed to send Telegram notification to {chat_id}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending Telegram notification: {str(e)}", exc_info=True)
            return False
    
    async def format_submission_message(
        self,
        form_title: str,
        user_name: str,
        user_email: Optional[str],
        submitted_at: str,
        field_values: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Format submission notification message for Telegram.
        
        Args:
            submission_id: Submission ID
            form_title: Form title
            user_name: Name of user who submitted
            user_email: Email of user (optional)
            submitted_at: Submission timestamp
            view_url: URL to view submission details
            field_values: List of field values with labels
            
        Returns:
            Formatted HTML message
        """
        email_part = f"\n📧 <b>Email:</b> {user_email}" if user_email else ""
        
        message = f"""🔔 <b>New Submission!</b>

📋 <b>Form:</b> {form_title}
👤 <b>Submitted by:</b> {user_name}{email_part}
⏰ <b>Time:</b> {submitted_at}
"""
        
        # Add form fields
        if field_values:
            message += "\n\n<b>📝 Submitted Data:</b>\n"
            for field in field_values:
                label = field.get('label', 'Unknown')
                value = field.get('value', 'N/A')
                field_type = field.get('type', '')
                
                # Format value based on field type
                if field_type == 'file':
                    file_count = field.get('file_count', 0)
                    value = f"📎 {file_count} file(s) uploaded"
                elif field_type == 'signature':
                    value = "✍️ [Digital Signature]"
                elif not value or value == '':
                    value = "<i>Not provided</i>"
                else:
                    # Escape HTML and truncate long values
                    value = str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    if len(value) > 100:
                        value = value[:97] + "..."
                
                message += f"\n• <b>{label}:</b> {value}"
        
        return message.strip()
