"""API routes module."""

from app.api.routes.forms import router as forms_router
from app.api.routes.users import router as users_router
from app.api.routes.auth import router as auth_router
from app.api.routes.super_admin import router as super_admin_router

__all__ = ["forms_router", "users_router", "auth_router", "super_admin_router"]

