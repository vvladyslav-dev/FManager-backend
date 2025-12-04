from starlette.types import ASGIApp, Receive, Scope, Send
from app.core.database import AsyncSessionLocal
from app.core.container import container
from app.core.deferred_event_bus import DeferredEventBus

class ContainerSessionMiddleware:
    """
    Pure ASGI middleware that creates a DB session and DI container override per request.
    
    Features:
    - Automatically commits transactions for mutating methods (POST, PUT, DELETE, PATCH)
    - Skips session creation for OPTIONS and HEAD requests (optimization)
    - Closes session properly in finally block
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        # Skip session creation for OPTIONS and HEAD requests
        if scope["type"] == "http" and scope["method"] in ("OPTIONS", "HEAD"):
            await self.app(scope, receive, send)
            return

        scope.setdefault("state", {})

        session = AsyncSessionLocal()
        # Wrap the global EventBus with a per-request deferred bus
        base_bus = container.event_bus()
        deferred_bus = DeferredEventBus(base_bus)
        
        try:
            with container.db_session.override(session), container.event_bus.override(deferred_bus):
                # Expose container on request state for dependencies
                scope.setdefault("state", {})
                scope["state"]["container"] = container
                await self.app(scope, receive, send)
                
                # Auto-commit for mutating methods if session is still active
                if scope["type"] == "http" and scope["method"] in ("POST", "PUT", "DELETE", "PATCH"):
                    if session.is_active:
                        await session.commit()
                        # After successful commit, flush deferred events
                        await deferred_bus.flush()
        except Exception:
            # Rollback on any exception
            if session.is_active:
                await session.rollback()
            raise
        finally:
            await session.close()