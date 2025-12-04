from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from uuid import UUID


class INotificationService(ABC):
    """Interface for notification service."""
    
    @abstractmethod
    async def send_notification(
        self,
        chat_id: str,
        message: str,
        parse_mode: Optional[str] = "HTML"
    ) -> bool:
        """
        Send notification to a user.
        
        Args:
            chat_id: Telegram chat ID or email address
            message: Message content
            parse_mode: Message formatting mode (HTML, Markdown, etc.)
            
        Returns:
            True if notification sent successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def format_submission_message(
        self,
        submission_id: UUID,
        form_title: str,
        user_name: str,
        user_email: Optional[str],
        submitted_at: str,
        view_url: str,
        field_values: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Format submission notification message.
        
        Args:
            submission_id: Submission ID
            form_title: Form title
            user_name: Name of user who submitted
            user_email: Email of user (optional)
            submitted_at: Submission timestamp
            view_url: URL to view submission details
            field_values: List of field values with labels
            
        Returns:
            Formatted message string
        """
        pass
