from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import importlib
import pkgutil
import logging
import sys

from app.core.config import settings
from app.api.routes import forms_router, users_router, auth_router, super_admin_router
from app.core.container import container
from app.core.middleware import ContainerSessionMiddleware
import app.application.handlers as handlers_pkg
from app.core.container import container
from app.domain.events.submission_events import SubmissionCreatedEvent
from app.application.handlers.notifications.telegram_notification_handler import TelegramNotificationHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True
)

logger = logging.getLogger(__name__)


def _import_all_submodules(package):
    """Import all submodules to register handlers with Mediator."""
    logger.info(f"Registering handlers from package: {package.__name__}")
    imported_count = 0
    for module_info in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        try:
            importlib.import_module(module_info.name)
            imported_count += 1
            logger.debug(f"Imported handler module: {module_info.name}")
        except Exception as e:
            logger.error(f"Failed to import handler module {module_info.name}: {e}")
            raise
    logger.info(f"Successfully registered {imported_count} handler modules")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for FastAPI app"""
    # Startup
    logger.info("Starting application...")
    
    # Import all handlers to register with Mediator
    _import_all_submodules(handlers_pkg)
    
    # Wire DI container
    container.wire(packages=["app.application.handlers"])
    
    # Subscribe event handlers (avoid importing handlers in container to prevent cycles)
    bus = container.event_bus()
    if settings.telegram_bot_token:
        telegram_handler = TelegramNotificationHandler(
            notification_service=container.telegram_notification_service()
        )
        bus.subscribe(SubmissionCreatedEvent, telegram_handler.handle)
        logger.info("Telegram notification handler subscribed to events")
    else:
        logger.info("Telegram bot token not configured, skipping notification handler")

    bot_service = container.telegram_bot_polling_service()
    await bot_service.start()
    yield
    # Shutdown
    logger.info("Shutting down application...")
    await bot_service.stop()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url="/redoc" if settings.environment != "production" else None,
    openapi_url="/openapi.json" if settings.environment != "production" else None
)

# Per-request DB session + DI container middleware
app.add_middleware(ContainerSessionMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(forms_router, prefix="/api/v1", tags=["Forms"])
app.include_router(users_router, prefix="/api/v1", tags=["Users"])
app.include_router(super_admin_router, prefix="/api/v1", tags=["Super Admin"])


@app.get("/")
async def root():
    return {
        "message": "Form Manager API",
        "version": settings.app_version
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}

