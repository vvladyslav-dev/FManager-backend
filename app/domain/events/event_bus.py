from typing import Type, Callable, Dict, List, Any
import logging
from app.domain.events.base_event import DomainEvent


logger = logging.getLogger(__name__)


class EventBus:
    """Simple in-memory event bus for domain events."""
    
    def __init__(self):
        self._subscribers: Dict[Type[DomainEvent], List[Callable]] = {}
    
    def subscribe(self, event_type: Type[DomainEvent], handler: Callable) -> None:
        """
        Subscribe a handler to an event type.
        
        Args:
            event_type: The type of event to subscribe to
            handler: Async callable that will handle the event
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append(handler)
        logger.info(f"Subscribed {handler.__class__.__name__} to {event_type.__name__}")
    
    async def publish(self, event: DomainEvent) -> None:
        """
        Publish an event to all subscribed handlers.
        
        Args:
            event: The domain event to publish
        """
        event_type = type(event)
        handlers = self._subscribers.get(event_type, [])
        
        if not handlers:
            logger.warning(f"No handlers registered for {event_type.__name__}")
            return
        
        logger.info(f"Publishing {event_type.__name__} to {len(handlers)} handler(s)")
        
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                # Log error but continue processing other handlers
                logger.error(
                    f"Error in handler {handler.__class__.__name__} "
                    f"for event {event_type.__name__}: {str(e)}",
                    exc_info=True
                )
    
    def clear_subscribers(self) -> None:
        """Clear all subscribers (useful for testing)."""
        self._subscribers.clear()
