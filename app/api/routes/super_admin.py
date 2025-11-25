from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.container import create_container_with_session
from app.core.dependencies import get_current_super_admin
from app.application.handlers.users.get_unapproved_admins_handler import GetUnapprovedAdminsHandler, GetUnapprovedAdminsRequest
from app.application.handlers.users.approve_admin_handler import ApproveAdminHandler, ApproveAdminRequest
from app.application.handlers.users.reject_admin_handler import RejectAdminHandler, RejectAdminRequest
from app.api.schemas import UserSchema
from app.domain.models import User

router = APIRouter(tags=["Super Admin"])


# Dependency injection functions using container
def get_get_unapproved_admins_handler(db: AsyncSession = Depends(get_db)) -> GetUnapprovedAdminsHandler:
    cont = create_container_with_session(db)
    return cont.get_unapproved_admins_handler()


def get_approve_admin_handler(db: AsyncSession = Depends(get_db)) -> ApproveAdminHandler:
    cont = create_container_with_session(db)
    return cont.approve_admin_handler()


def get_reject_admin_handler(db: AsyncSession = Depends(get_db)) -> RejectAdminHandler:
    cont = create_container_with_session(db)
    return cont.reject_admin_handler()


@router.get("/super-admin/unapproved-admins", response_model=list[UserSchema])
async def get_unapproved_admins(
    current_user: User = Depends(get_current_super_admin),
    handler: GetUnapprovedAdminsHandler = Depends(get_get_unapproved_admins_handler)
):
    """Get all unapproved admin users (super admin only)"""
    use_case_request = GetUnapprovedAdminsRequest()
    response = await handler.handle(use_case_request)
    return response.admins


@router.post("/super-admin/admins/{user_id}/approve", response_model=UserSchema)
async def approve_admin(
    user_id: UUID,
    current_user: User = Depends(get_current_super_admin),
    handler: ApproveAdminHandler = Depends(get_approve_admin_handler)
):
    """Approve an admin user registration (super admin only)"""
    use_case_request = ApproveAdminRequest(user_id=user_id)
    try:
        response = await handler.handle(use_case_request)
        return response.user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/super-admin/admins/{user_id}/reject")
async def reject_admin(
    user_id: UUID,
    current_user: User = Depends(get_current_super_admin),
    handler: RejectAdminHandler = Depends(get_reject_admin_handler)
):
    """Reject an admin user registration (super admin only)"""
    use_case_request = RejectAdminRequest(user_id=user_id)
    try:
        response = await handler.handle(use_case_request)
        return {"success": response.success}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


