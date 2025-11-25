from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.container import create_container_with_session
from app.application.handlers.users.create_user_handler import CreateUserHandler, CreateUserRequest
from app.application.handlers.users.get_user_handler import GetUserHandler, GetUserRequest
from app.application.handlers.users.list_users_by_admin_handler import ListUsersByAdminHandler, ListUsersByAdminRequest
from app.application.handlers.users.update_user_handler import UpdateUserHandler, UpdateUserRequest
from app.application.handlers.users.delete_user_handler import DeleteUserHandler, DeleteUserRequest
from app.api.schemas import (
    UserSchema,
    CreateUserRequest as CreateUserAPIRequest,
    UpdateUserRequest as UpdateUserAPIRequest
)

router = APIRouter(tags=["Users"])


# Dependency injection functions using container
def get_create_user_handler(db: AsyncSession = Depends(get_db)) -> CreateUserHandler:
    cont = create_container_with_session(db)
    return cont.create_user_handler()


def get_get_user_handler(db: AsyncSession = Depends(get_db)) -> GetUserHandler:
    cont = create_container_with_session(db)
    return cont.get_user_handler()


def get_list_users_by_admin_handler(db: AsyncSession = Depends(get_db)) -> ListUsersByAdminHandler:
    cont = create_container_with_session(db)
    return cont.list_users_by_admin_handler()


def get_update_user_handler(db: AsyncSession = Depends(get_db)) -> UpdateUserHandler:
    cont = create_container_with_session(db)
    return cont.update_user_handler()


def get_delete_user_handler(db: AsyncSession = Depends(get_db)) -> DeleteUserHandler:
    cont = create_container_with_session(db)
    return cont.delete_user_handler()


@router.post("/users", response_model=UserSchema)
async def create_user(
    request: CreateUserAPIRequest,
    handler: CreateUserHandler = Depends(get_create_user_handler)
):
    """Create a new user"""
    use_case_request = CreateUserRequest(
        name=request.name,
        email=request.email,
        is_admin=request.is_admin,
        admin_id=request.admin_id
    )
    try:
        response = await handler.handle(use_case_request)
        return response.user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/users/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: UUID,
    handler: GetUserHandler = Depends(get_get_user_handler)
):
    """Get user by ID"""
    use_case_request = GetUserRequest(user_id=user_id)
    response = await handler.handle(use_case_request)
    if not response.user:
        raise HTTPException(status_code=404, detail="User not found")
    return response.user


@router.get("/admin/{admin_id}/users", response_model=list[UserSchema])
async def list_users_by_admin(
    admin_id: UUID,
    handler: ListUsersByAdminHandler = Depends(get_list_users_by_admin_handler)
):
    """Get all users for an admin"""
    use_case_request = ListUsersByAdminRequest(admin_id=admin_id)
    response = await handler.handle(use_case_request)
    return response.users


@router.put("/users/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: UUID,
    request: UpdateUserAPIRequest,
    handler: UpdateUserHandler = Depends(get_update_user_handler)
):
    """Update a user"""
    use_case_request = UpdateUserRequest(
        user_id=user_id,
        name=request.name,
        email=request.email,
        is_admin=request.is_admin
    )
    try:
        response = await handler.handle(use_case_request)
        return response.user
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: UUID,
    handler: DeleteUserHandler = Depends(get_delete_user_handler)
):
    """Delete a user"""
    use_case_request = DeleteUserRequest(user_id=user_id)
    try:
        response = await handler.handle(use_case_request)
        return {"success": response.success}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

