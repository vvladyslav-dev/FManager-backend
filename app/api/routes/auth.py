from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.container import create_container_with_session
from app.application.handlers.auth.register_handler import RegisterHandler, RegisterRequest
from app.application.handlers.auth.login_handler import LoginHandler, LoginRequest
from app.api.schemas import RegisterRequest as RegisterAPIRequest, LoginRequest as LoginAPIRequest

router = APIRouter(tags=["Auth"])


# Dependency injection functions using container
def get_register_handler(db: AsyncSession = Depends(get_db)) -> RegisterHandler:
    cont = create_container_with_session(db)
    return cont.register_handler()


def get_login_handler(db: AsyncSession = Depends(get_db)) -> LoginHandler:
    cont = create_container_with_session(db)
    return cont.login_handler()


@router.post("/register")
async def register(
    request: RegisterAPIRequest,
    handler: RegisterHandler = Depends(get_register_handler)
):
    """Register a new user"""
    try:
        use_case_request = RegisterRequest(
            email=request.email,
            password=request.password,
            name=request.name,
            is_admin=request.is_admin
        )
        response = await handler.handle(use_case_request)
        return {
            "access_token": response.access_token,
            "token_type": response.token_type,
            "user": response.user
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
async def login(
    request: LoginAPIRequest,
    handler: LoginHandler = Depends(get_login_handler)
):
    """Login user"""
    try:
        use_case_request = LoginRequest(
            email=request.email,
            password=request.password
        )
        response = await handler.handle(use_case_request)
        return {
            "access_token": response.access_token,
            "token_type": response.token_type,
            "user": response.user
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

