from typing import cast
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from mediatr import Mediator

from app.core.dependencies import get_current_super_admin
from app.application.handlers.users.get_unapproved_admins_handler import GetUnapprovedAdminsRequest, GetUnapprovedAdminsResponse
from app.application.handlers.users.approve_admin_handler import ApproveAdminRequest, ApproveAdminResponse
from app.application.handlers.users.reject_admin_handler import RejectAdminRequest, RejectAdminResponse
from app.api.schemas import UserSchema
from app.domain.models import User

router = APIRouter(tags=["Super Admin"])


@router.get("/super-admin/unapproved-admins", response_model=GetUnapprovedAdminsResponse)
async def get_unapproved_admins(
    current_user: User = Depends(get_current_super_admin),
):
    """Get all unapproved admin users (super admin only)"""
    use_case_request = GetUnapprovedAdminsRequest()
    response = cast(GetUnapprovedAdminsResponse, await Mediator.send_async(use_case_request))
    return response


@router.post("/super-admin/admins/{user_id}/approve", response_model=ApproveAdminResponse)
async def approve_admin(
    user_id: UUID,
    current_user: User = Depends(get_current_super_admin),
):
    """Approve an admin user registration (super admin only)"""
    use_case_request = ApproveAdminRequest(user_id=user_id)
    try:
        response = cast(ApproveAdminResponse, await Mediator.send_async(use_case_request))
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/super-admin/admins/{user_id}/reject", response_model=RejectAdminResponse)
async def reject_admin(
    user_id: UUID,
    current_user: User = Depends(get_current_super_admin),
):
    """Reject an admin user registration (super admin only)"""
    use_case_request = RejectAdminRequest(user_id=user_id)
    try:
        response = cast(RejectAdminResponse, await Mediator.send_async(use_case_request))
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


