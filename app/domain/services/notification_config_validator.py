"""Domain service for validating notification channel configs"""
from typing import Dict, Any, Type
from pydantic import BaseModel, ValidationError

from app.domain.models import NotificationChannelType
from app.domain.schemas.notification_configs import TelegramChannelConfig


class NotificationConfigValidator:
    """Validates notification channel configs against their schemas"""
    
    CHANNEL_CONFIG_SCHEMAS: Dict[NotificationChannelType, Type[BaseModel]] = {
        NotificationChannelType.TELEGRAM: TelegramChannelConfig,
    }
    
    @classmethod
    def validate(cls, channel_type: NotificationChannelType, config: Dict[str, Any]) -> BaseModel:
        """
        Validate config against the schema for the given channel type.
        
        Args:
            channel_type: The notification channel type
            config: The configuration dict to validate
            
        Returns:
            Validated Pydantic model instance
            
        Raises:
            ValueError: If channel type is not supported or config is invalid
        """
        schema = cls.CHANNEL_CONFIG_SCHEMAS.get(channel_type)
        if not schema:
            raise ValueError(f"Unsupported channel type: {channel_type}")
        
        try:
            return schema(**config)
        except ValidationError as e:
            raise ValueError(f"Invalid config for {channel_type.value}: {e}")
    
    @classmethod
    def get_schema(cls, channel_type: NotificationChannelType) -> Type[BaseModel]:
        """Get the Pydantic schema for a channel type"""
        schema = cls.CHANNEL_CONFIG_SCHEMAS.get(channel_type)
        if not schema:
            raise ValueError(f"Unsupported channel type: {channel_type}")
        return schema
