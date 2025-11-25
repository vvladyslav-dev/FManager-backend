from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import forms_router, users_router, auth_router, super_admin_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)

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

