from typing import cast
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from mediatr import Mediator

from app.core.dependencies import get_current_user
from app.application.handlers.users.create_user_handler import CreateUserRequest, CreateUserResponse
from app.application.handlers.users.get_user_handler import GetUserRequest, GetUserResponse
from app.application.handlers.users.list_users_by_admin_handler import ListUsersByAdminRequest, ListUsersByAdminResponse
from app.application.handlers.users.update_user_handler import UpdateUserRequest, UpdateUserResponse
from app.application.handlers.users.delete_user_handler import DeleteUserRequest, DeleteUserResponse
from app.application.handlers.notifications.get_notification_settings_handler import (
    GetNotificationSettingsRequest,
    GetNotificationSettingsResponse
)
from app.application.handlers.notifications.update_notification_settings_handler import (
    UpdateNotificationSettingsRequest,
    UpdateNotificationSettingsResponse
)
from app.domain.models import User
from fastapi import UploadFile, File as FastAPIFile
from app.application.handlers.users.upload_avatar_handler import (
    UploadAvatarRequest,
    UploadAvatarResponse,
)

router = APIRouter(tags=["Users"])


@router.post("/users", response_model=CreateUserResponse)
async def create_user(
    request: CreateUserRequest,
):
    """Create a new user"""
    try:
        response = cast(CreateUserResponse, await Mediator.send_async(request))
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/users/{user_id}", response_model=GetUserResponse)
async def get_user(
    user_id: UUID,
):
    """Get user by ID"""
    use_case_request = GetUserRequest(user_id=user_id)
    response = cast(GetUserResponse, await Mediator.send_async(use_case_request))
    if not response.user:
        raise HTTPException(status_code=404, detail="User not found")
    return response


@router.get("/admin/{admin_id}/users", response_model=ListUsersByAdminResponse)
async def list_users_by_admin(
    admin_id: UUID,
):
    """Get all users for an admin"""
    use_case_request = ListUsersByAdminRequest(admin_id=admin_id)
    response = cast(ListUsersByAdminResponse, await Mediator.send_async(use_case_request))
    return response


@router.put("/users/{user_id}", response_model=UpdateUserResponse)
async def update_user(
    user_id: UUID,
    request: UpdateUserRequest,
):
    """Update a user"""
    try:
        response = cast(UpdateUserResponse, await Mediator.send_async(request))
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/users/{user_id}", response_model=DeleteUserResponse)
async def delete_user(
    user_id: UUID,
):
    """Delete a user"""
    use_case_request = DeleteUserRequest(user_id=user_id)
    try:
        response = cast(DeleteUserResponse, await Mediator.send_async(use_case_request))
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/users/{user_id}/notification-settings", response_model=GetNotificationSettingsResponse)
async def get_notification_settings(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
):
    """Get notification settings for a user"""
    # Only allow users to get their own settings or super admins
    if current_user.id != user_id and not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        request = GetNotificationSettingsRequest(user_id=user_id)
        response = cast(GetNotificationSettingsResponse, await Mediator.send_async(request))
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/users/{user_id}/notification-settings", response_model=UpdateNotificationSettingsResponse)
async def update_notification_settings(
    user_id: UUID,
    request: dict,
    current_user: User = Depends(get_current_user),
):
    """Update notification settings for a user"""
    # Only allow users to update their own settings or super admins
    if current_user.id != user_id and not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        mapped = UpdateNotificationSettingsRequest(
            user_id=user_id,
            telegram_chat_id=request.get("telegram_chat_id"),
            telegram_notifications_enabled=request.get("telegram_notifications_enabled"),
            email_notifications_enabled=request.get("email_notifications_enabled"),
        )
        response = cast(UpdateNotificationSettingsResponse, await Mediator.send_async(mapped))
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/users/{user_id}/avatar", response_model=UploadAvatarResponse)
async def upload_avatar(
    user_id: UUID,
    file: UploadFile = FastAPIFile(...),
    current_user: User = Depends(get_current_user),
):
    """Upload avatar for current user and update avatar_url."""
    if current_user.id != user_id and not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    content = await file.read()
    request = UploadAvatarRequest(
        user_id=user_id,
        filename=file.filename,
        content_type=file.content_type,
        content=content,
        file_size=file.size,
    )
    try:
        response = cast(UploadAvatarResponse, await Mediator.send_async(request))
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

