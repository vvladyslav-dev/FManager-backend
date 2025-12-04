"""Pydantic schemas for notification channel configs"""
from pydantic import BaseModel, Field, field_validator


class TelegramChannelConfig(BaseModel):
    """Telegram notification channel configuration"""
    chat_id: str = Field(..., min_length=1, description="Telegram chat ID")
    
    @field_validator('chat_id')
    @classmethod
    def validate_chat_id(cls, v: str) -> str:
        """Ensure chat_id is not empty"""
        if not v or not v.strip():
            raise ValueError("chat_id cannot be empty")
        return v.strip()
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "chat_id": "123456789"
            }
        }
    }
