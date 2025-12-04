from typing import cast
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File as FastAPIFile, Form, Response, Query
import unicodedata
from urllib.parse import quote
import os
from mediatr import Mediator
import logging
import traceback
from datetime import datetime

from app.application.handlers.forms.create_form_handler import CreateFormRequest, CreateFormResponse
from app.application.handlers.forms.get_form_handler import GetFormRequest, GetFormResponse
from app.application.handlers.forms.get_forms_by_creator_handler import GetFormsByCreatorRequest, GetFormsByCreatorResponse
from app.application.handlers.forms.update_form_handler import UpdateFormRequest, UpdateFormResponse
from app.application.handlers.forms.delete_form_handler import DeleteFormRequest, DeleteFormResponse
from app.application.handlers.submissions.submit_form_handler import SubmitFormRequest, SubmitFormResponse
from app.application.handlers.submissions.get_submissions_by_admin_handler import GetSubmissionsByAdminRequest, GetSubmissionsByAdminResponse
from app.application.handlers.submissions.get_submissions_by_form_handler import GetSubmissionsByFormRequest, GetSubmissionsByFormResponse
from app.application.handlers.submissions.get_submission_handler import GetSubmissionRequest, GetSubmissionResponse
from app.application.handlers.submissions.delete_submission_handler import DeleteSubmissionRequest, DeleteSubmissionResponse
from app.application.handlers.submissions.export_submission_handler import ExportSubmissionRequest
from app.application.handlers.submissions.get_submission_count_handler import GetSubmissionCountRequest, GetSubmissionCountResponse
from app.application.handlers.files.view_file_handler import ViewFileRequest, ViewFileResponse
from app.core.dependencies import get_current_user
from app.domain.models import User

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Forms"])


@router.get("/forms/{form_id}/submissions/count", response_model=GetSubmissionCountResponse)
async def get_submission_count(
    form_id: UUID,
):
    """Get submission count for a specific form"""
    use_case_request = GetSubmissionCountRequest(form_id=form_id)
    response = cast(GetSubmissionCountResponse, await Mediator.send_async(use_case_request))
    return response


@router.post("/forms", response_model=CreateFormResponse)
async def create_form(
    request: CreateFormRequest,
    current_user: User = Depends(get_current_user),
):
    """Create a new form (admin only)"""
    # Set creator_id from authenticated user
    request.creator_id = current_user.id
    response = cast(CreateFormResponse, await Mediator.send_async(request))
    return response


@router.get("/forms/{form_id}", response_model=GetFormResponse)
async def get_form(
    form_id: UUID,
):
    """Get form by ID (public endpoint, no auth required)"""
    use_case_request = GetFormRequest(form_id=form_id)
    response = cast(GetFormResponse, await Mediator.send_async(use_case_request))
    # Return 200 with form=None when not found (for public access)
    return response


@router.post("/forms/{form_id}/submit", response_model=SubmitFormResponse)
async def submit_form(
    form_id: UUID,
    user_name: str = Form(...),
    user_email: str | None = Form(None),
    field_values_json: str | None = Form(None),  # JSON string
    file_fields_json: str | None = Form(None),  # JSON string mapping file index to field_id
    files: list[UploadFile] | None = FastAPIFile(None),
):
    """Submit a form (public endpoint, no auth required)
    
    field_values should be JSON like {"field-uuid-1": "value1", "field-uuid-2": "value2"}
    file_fields should be JSON like {"0": "field-uuid-1", "1": "field-uuid-2"} mapping file index to field_id
    """
    use_case_request = SubmitFormRequest(
        form_id=form_id,
        user_name=user_name,
        user_email=user_email,
        field_values_json=field_values_json,
        file_fields_json=file_fields_json,
        files=files
    )
    
    try:
        response = cast(SubmitFormResponse, await Mediator.send_async(use_case_request))
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error submitting form: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/admin/{admin_id}/submissions", response_model=GetSubmissionsByAdminResponse)
async def get_submissions_by_admin(
    admin_id: UUID,
    skip: int = 0,
    limit: int = 10,
    date_from: datetime | None = Query(None, description="Filter submissions from this date"),
    date_to: datetime | None = Query(None, description="Filter submissions until this date"),
    user_name: str | None = Query(None, description="Filter by user name (partial match)"),
    user_email: str | None = Query(None, description="Filter by user email (partial match)"),
    field_value_search: str | None = Query(None, description="Search in form field values"),
    form_id: UUID | None = Query(None, description="Filter by form ID"),
):
    """Get all submissions for forms created by admin or submitted by users linked to admin"""
    use_case_request = GetSubmissionsByAdminRequest(
        admin_id=admin_id,
        skip=skip,
        limit=limit,
        date_from=date_from,
        date_to=date_to,
        user_name=user_name,
        user_email=user_email,
        field_value_search=field_value_search,
        form_id=form_id
    )
    response = cast(GetSubmissionsByAdminResponse, await Mediator.send_async(use_case_request))
    return response


@router.get("/forms/{form_id}/submissions", response_model=GetSubmissionsByFormResponse)
async def get_submissions_by_form(
    form_id: UUID,
):
    """Get all submissions for a specific form"""
    use_case_request = GetSubmissionsByFormRequest(form_id=form_id)
    response = cast(GetSubmissionsByFormResponse, await Mediator.send_async(use_case_request))
    return response


@router.get("/submissions/{submission_id}", response_model=GetSubmissionResponse)
async def get_submission(
    submission_id: UUID,
):
    """Get a submission by ID"""
    try:
        use_case_request = GetSubmissionRequest(submission_id=submission_id)
        response = cast(GetSubmissionResponse, await Mediator.send_async(use_case_request))
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/submissions/{submission_id}", response_model=DeleteSubmissionResponse)
async def delete_submission(
    submission_id: UUID,
):
    """Delete a submission"""
    try:
        use_case_request = DeleteSubmissionRequest(submission_id=submission_id)
        response = cast(DeleteSubmissionResponse, await Mediator.send_async(use_case_request))
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/submissions/{submission_id}/export")
async def export_submission(
    submission_id: UUID,
    format: str = Query(..., regex="^(csv|xlsx)$", description="Export format: csv or xlsx"),
    locale: str = Query("en", description="Locale: en or uk (defaults to en for unknown values)"),
):
    """Export a submission to CSV or XLSX format"""
    # Validate locale, fallback to 'en' if unknown
    if locale not in ["en", "uk"]:
        locale = "en"
    
    try:
        use_case_request = ExportSubmissionRequest(
            submission_id=submission_id,
            format=format,  # type: ignore
            locale=locale
        )
        response = await Mediator.send_async(use_case_request)
        
        # Build RFC 6266 compliant Content-Disposition for non-ASCII filenames
        original_filename = response.filename
        # ASCII fallback by stripping accents/non-ascii
        ascii_fallback = unicodedata.normalize('NFKD', original_filename).encode('ascii', 'ignore').decode('ascii')
        if not ascii_fallback:
            base, ext = os.path.splitext(original_filename)
            ascii_fallback = f"export{ext or ''}"  # ensure non-empty fallback
        encoded_utf8 = quote(original_filename.encode('utf-8'))

        content_disposition = (
            f"attachment; filename=\"{ascii_fallback}\"; filename*=UTF-8''{encoded_utf8}"
        )

        return Response(
            content=response.file_buffer.getvalue(),
            media_type=response.media_type,
            headers={
                "Content-Disposition": content_disposition,
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/admin/{creator_id}/forms", response_model=GetFormsByCreatorResponse)
async def get_forms_by_creator(
    creator_id: UUID,
    skip: int = 0,
    limit: int = 10,
):
    """Get all forms created by a specific creator (admin only)"""
    use_case_request = GetFormsByCreatorRequest(creator_id=creator_id, skip=skip, limit=limit)
    response = cast(GetFormsByCreatorResponse, await Mediator.send_async(use_case_request))
    return response


@router.put("/forms/{form_id}", response_model=UpdateFormResponse)
async def update_form(
    form_id: UUID,
    body: dict,
):
    """Update a form"""
    try:
        # Create request with form_id from path
        request = UpdateFormRequest(
            form_id=form_id,
            title=body.get("title"),
            description=body.get("description"),
            fields=body.get("fields")
        )
        response = cast(UpdateFormResponse, await Mediator.send_async(request))
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/forms/{form_id}", response_model=DeleteFormResponse)
async def delete_form(
    form_id: UUID,
):
    """Delete a form"""
    try:
        use_case_request = DeleteFormRequest(form_id=form_id)
        response = cast(DeleteFormResponse, await Mediator.send_async(use_case_request))
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/files/{file_id}/view")
async def view_file(
    file_id: UUID,
):
    """View/download a file by ID. Supports inline viewing for PDFs, images, text files."""
    try:
        use_case_request = ViewFileRequest(file_id=file_id)
        response = cast(ViewFileResponse, await Mediator.send_async(use_case_request))
        
        # Build RFC 6266 compliant Content-Disposition for non-ASCII filenames
        original_filename = response.filename
        ascii_fallback = unicodedata.normalize('NFKD', original_filename).encode('ascii', 'ignore').decode('ascii')
        if not ascii_fallback:
            base, ext = os.path.splitext(original_filename)
            ascii_fallback = f"download{ext or ''}"
        encoded_utf8 = quote(original_filename.encode('utf-8'))
        content_disposition = (
            f"{response.disposition}; filename=\"{ascii_fallback}\"; filename*=UTF-8''{encoded_utf8}"
        )

        return Response(
            content=response.content,
            media_type=response.content_type,
            headers={
                "Content-Disposition": content_disposition,
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error downloading file {file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")

