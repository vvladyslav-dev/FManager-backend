from typing import cast
from fastapi import APIRouter, HTTPException
from mediatr import Mediator
from app.application.handlers.auth.register_handler import RegisterRequest, RegisterResponse
from app.application.handlers.auth.login_handler import LoginRequest, LoginResponse
from app.application.handlers.auth.change_password_handler import (
    ChangePasswordRequest,
    ChangePasswordResponse,
)
from fastapi import Depends
from app.core.dependencies import get_current_user
from app.domain.models import User

router = APIRouter(tags=["Auth"])


@router.post("/register", response_model=RegisterResponse)
async def register(
    request: RegisterRequest,
):
    """Register a new user"""
    try:
        response = cast(RegisterResponse, await Mediator.send_async(request))
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
):
    """Login user"""
    try:
        response = cast(LoginResponse, await Mediator.send_async(request))
        return response
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/change-password", response_model=ChangePasswordResponse)
async def change_password(
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Change current user's password."""
    try:
        # Accept frontend payload keys old_password/new_password and map to handler
        mapped = ChangePasswordRequest(
            user_id=str(current_user.id),
            current_password=request.get("old_password") or request.get("current_password"),
            new_password=request.get("new_password"),
        )
        response = cast(ChangePasswordResponse, await Mediator.send_async(mapped))
        return response
    except ValueError as e:
        # bad request or unauthorized depending on message; keep 400 for simplicity
        raise HTTPException(status_code=400, detail=str(e))

