from typing import List
from app.domain.events.base_event import DomainEvent
from app.domain.events.event_bus import EventBus


class DeferredEventBus(EventBus):
    """
    Wrapper around EventBus that defers publishing until explicitly flushed.
    Collects events per-request and flushes them after a successful commit.
    """

    def __init__(self, underlying: EventBus):
        super().__init__()
        # Reuse subscribers from the underlying bus
        self._subscribers = underlying._subscribers
        self._underlying = underlying
        self._queue: List[DomainEvent] = []

    async def publish(self, event: DomainEvent) -> None:
        # Defer event publication until flush() is called
        self._queue.append(event)

    async def flush(self) -> None:
        # Publish all queued events via underlying bus
        while self._queue:
            event = self._queue.pop(0)
            await self._underlying.publish(event)
