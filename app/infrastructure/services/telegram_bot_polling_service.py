import logging
from uuid import uuid4
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from app.core.database import AsyncSessionLocal
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.notification_channel_repository import NotificationChannelRepository
from app.domain.models import NotificationChannel, NotificationChannelType

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    chat_id = str(update.effective_chat.id)
    
    response_text = (
        "👋 <b>Welcome to Form Manager Bot!</b>\n\n"
        f"📋 <b>Your Chat ID:</b> <code>{chat_id}</code>\n\n"
        "📝 <b>How to enable notifications:</b>\n"
        "1️⃣ Copy your Chat ID (tap to copy)\n"
        "2️⃣ Open Form Manager → Settings\n"
        "3️⃣ Paste your Chat ID\n"
        "4️⃣ Click Save and enable notifications\n\n"
        "✅ You'll receive instant alerts when new forms are submitted!\n\n"
        "💡 <b>Commands:</b>\n"
        "/start - Show this message\n"
        "/stop - Disable notifications"
    )
    
    await update.message.reply_text(response_text, parse_mode="HTML")
    logger.info(f"Sent Chat ID to user: {chat_id}")


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /stop command"""
    chat_id = str(update.effective_chat.id)
    
    # Create database session
    async with AsyncSessionLocal() as session:
        user_repo = UserRepository(session)
        channel_repo = NotificationChannelRepository(session)
        
        # Find user by chat_id in notification channels
        # Since we don't have a direct method, we need to query differently
        # For now, we'll inform the user to disable via settings
        
        response_text = (
            "🔕 <b>To disable notifications:</b>\n\n"
            "1️⃣ Open Form Manager → Settings\n"
            "2️⃣ Toggle off Telegram notifications\n\n"
            "💡 You can re-enable them anytime!"
        )
    
    await update.message.reply_text(response_text, parse_mode="HTML")


class TelegramBotPollingService:
    """Infrastructure service to run Telegram bot in polling mode"""
    
    def __init__(self, bot_token: str):
        """
        Initialize Telegram bot polling service.
        
        Args:
            bot_token: Telegram bot token
        """
        self.application = None
        self.bot_token = bot_token
        self.enabled = bool(bot_token)
    
    async def start(self):
        """Start the bot in polling mode"""
        if not self.enabled:
            logger.info("Telegram bot token not configured, skipping bot startup")
            return
        
        try:
            # Create application
            self.application = Application.builder().token(self.bot_token).build()
            
            # Register command handlers
            self.application.add_handler(CommandHandler("start", start_command))
            self.application.add_handler(CommandHandler("stop", stop_command))
            
            # Start polling
            logger.info("Starting Telegram bot in polling mode...")
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling(drop_pending_updates=True)
            
            logger.info("Telegram bot is running!")
            
        except Exception as e:
            logger.error(f"Failed to start Telegram bot: {str(e)}", exc_info=True)
    
    async def stop(self):
        """Stop the bot"""
        if self.application:
            try:
                logger.info("Stopping Telegram bot...")
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
                logger.info("Telegram bot stopped")
            except Exception as e:
                logger.error(f"Error stopping Telegram bot: {str(e)}", exc_info=True)
