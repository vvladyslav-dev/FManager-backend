from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File as FastAPIFile, Form, Response, Query
from sqlalchemy.ext.asyncio import AsyncSession
import json
import logging
from datetime import datetime
from typing import Optional

from app.core.database import get_db
from app.core.container import create_container_with_session
from app.infrastructure.repositories.file_repository import FileRepository
from app.infrastructure.repositories.form_submission_repository import FormSubmissionRepository
from app.core.azure_storage import azure_storage_client
from app.application.handlers.forms.create_form_handler import CreateFormHandler, CreateFormRequest
from app.application.handlers.forms.get_form_handler import GetFormHandler, GetFormRequest
from app.application.handlers.forms.get_forms_by_creator_handler import GetFormsByCreatorHandler, GetFormsByCreatorRequest
from app.application.handlers.forms.update_form_handler import UpdateFormHandler, UpdateFormRequest
from app.application.handlers.forms.delete_form_handler import DeleteFormHandler, DeleteFormRequest
from app.application.handlers.submissions.submit_form_handler import SubmitFormHandler, SubmitFormRequest
from app.application.handlers.submissions.get_submissions_by_admin_handler import GetSubmissionsByAdminHandler, GetSubmissionsByAdminRequest
from app.application.handlers.submissions.get_submissions_by_form_handler import GetSubmissionsByFormHandler, GetSubmissionsByFormRequest
from app.application.handlers.submissions.delete_submission_handler import DeleteSubmissionHandler, DeleteSubmissionRequest
from app.api.schemas import (
    FormSchema,
    CreateFormRequest as CreateFormAPIRequest,
    UpdateFormRequest as UpdateFormAPIRequest,
    FormSubmissionSchema,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Forms"])


# Dependency injection functions using container
def get_create_form_handler(db: AsyncSession = Depends(get_db)) -> CreateFormHandler:
    cont = create_container_with_session(db)
    return cont.create_form_handler()


def get_get_form_handler(db: AsyncSession = Depends(get_db)) -> GetFormHandler:
    cont = create_container_with_session(db)
    return cont.get_form_handler()


def get_submit_form_handler(db: AsyncSession = Depends(get_db)) -> SubmitFormHandler:
    cont = create_container_with_session(db)
    return cont.submit_form_handler()


def get_submissions_by_admin_handler(db: AsyncSession = Depends(get_db)) -> GetSubmissionsByAdminHandler:
    cont = create_container_with_session(db)
    return cont.get_submissions_by_admin_handler()


def get_submissions_by_form_handler(db: AsyncSession = Depends(get_db)) -> GetSubmissionsByFormHandler:
    cont = create_container_with_session(db)
    return cont.get_submissions_by_form_handler()


def get_delete_submission_handler(db: AsyncSession = Depends(get_db)) -> DeleteSubmissionHandler:
    cont = create_container_with_session(db)
    return cont.delete_submission_handler()


def get_forms_by_creator_handler(db: AsyncSession = Depends(get_db)) -> GetFormsByCreatorHandler:
    cont = create_container_with_session(db)
    return cont.get_forms_by_creator_handler()


def get_update_form_handler(db: AsyncSession = Depends(get_db)) -> UpdateFormHandler:
    cont = create_container_with_session(db)
    return cont.update_form_handler()


def get_delete_form_handler(db: AsyncSession = Depends(get_db)) -> DeleteFormHandler:
    cont = create_container_with_session(db)
    return cont.delete_form_handler()


def get_file_repository(db: AsyncSession = Depends(get_db)) -> FileRepository:
    return FileRepository(db)


def get_form_submission_repository(db: AsyncSession = Depends(get_db)) -> FormSubmissionRepository:
    return FormSubmissionRepository(db)


@router.get("/forms/{form_id}/submissions/count")
async def get_submission_count(
    form_id: UUID,
    submission_repository: FormSubmissionRepository = Depends(get_form_submission_repository)
):
    """Get submission count for a specific form"""
    count = await submission_repository.count_by_form_id(form_id)
    return {"count": count}


@router.post("/forms", response_model=FormSchema)
async def create_form(
    request: CreateFormAPIRequest,
    creator_id: UUID,
    handler: CreateFormHandler = Depends(get_create_form_handler)
):
    """Create a new form (admin only)"""
    use_case_request = CreateFormRequest(
        title=request.title,
        description=request.description,
        creator_id=creator_id,
        fields=request.fields
    )
    response = await handler.handle(use_case_request)
    return response.form


@router.get("/forms/{form_id}", response_model=FormSchema)
async def get_form(
    form_id: UUID,
    handler: GetFormHandler = Depends(get_get_form_handler)
):
    """Get form by ID (public endpoint, no auth required)"""
    use_case_request = GetFormRequest(form_id=form_id)
    response = await handler.handle(use_case_request)
    if not response.form:
        raise HTTPException(status_code=404, detail="Form not found")
    return response.form


@router.post("/forms/{form_id}/submit", response_model=FormSubmissionSchema)
async def submit_form(
    form_id: UUID,
    user_name: str = Form(...),
    user_email: str | None = Form(None),
    field_values: str | None = Form(None),  # JSON string
    file_fields: str | None = Form(None),  # JSON string mapping file index to field_id
    files: list[UploadFile] | None = FastAPIFile(None),
    handler: SubmitFormHandler = Depends(get_submit_form_handler)
):
    """Submit a form (public endpoint, no auth required)
    
    field_values should be JSON like {"field-uuid-1": "value1", "field-uuid-2": "value2"}
    file_fields should be JSON like {"0": "field-uuid-1", "1": "field-uuid-2"} mapping file index to field_id
    """
    try:
        field_values_dict = json.loads(field_values) if field_values else {}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid field_values JSON")
    
    files_dict = {}
    if files and file_fields:
        try:
            file_fields_dict = json.loads(file_fields)
            for idx, file in enumerate(files):
                field_id_str = file_fields_dict.get(str(idx))
                if field_id_str:
                    content = await file.read()
                    files_dict[field_id_str] = {
                        "content": content,
                        "filename": file.filename or "file"
                    }
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid file_fields JSON: {str(e)}")
    elif files and not file_fields:
        # If files are provided but file_fields mapping is missing
        raise HTTPException(status_code=400, detail="file_fields mapping is required when files are uploaded")
    
    use_case_request = SubmitFormRequest(
        form_id=form_id,
        user_name=user_name,
        user_email=user_email,
        field_values=field_values_dict,
        files=files_dict if files_dict else None
    )
    
    try:
        response = await handler.handle(use_case_request)
        return response.submission
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        logger.error(f"Unexpected error submitting form: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/admin/{admin_id}/submissions", response_model=list[FormSubmissionSchema])
async def get_submissions_by_admin(
    admin_id: UUID,
    skip: int = 0,
    limit: int = 10,
    date_from: Optional[datetime] = Query(None, description="Filter submissions from this date"),
    date_to: Optional[datetime] = Query(None, description="Filter submissions until this date"),
    user_name: Optional[str] = Query(None, description="Filter by user name (partial match)"),
    user_email: Optional[str] = Query(None, description="Filter by user email (partial match)"),
    field_value_search: Optional[str] = Query(None, description="Search in form field values"),
    form_id: Optional[UUID] = Query(None, description="Filter by form ID"),
    handler: GetSubmissionsByAdminHandler = Depends(get_submissions_by_admin_handler)
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
    response = await handler.handle(use_case_request)
    return response.submissions


@router.get("/forms/{form_id}/submissions", response_model=list[FormSubmissionSchema])
async def get_submissions_by_form(
    form_id: UUID,
    handler: GetSubmissionsByFormHandler = Depends(get_submissions_by_form_handler)
):
    """Get all submissions for a specific form"""
    use_case_request = GetSubmissionsByFormRequest(form_id=form_id)
    response = await handler.handle(use_case_request)
    return response.submissions


@router.delete("/submissions/{submission_id}")
async def delete_submission(
    submission_id: UUID,
    handler: DeleteSubmissionHandler = Depends(get_delete_submission_handler)
):
    """Delete a submission"""
    try:
        use_case_request = DeleteSubmissionRequest(submission_id=submission_id)
        response = await handler.handle(use_case_request)
        return {"success": response.success}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/admin/{creator_id}/forms", response_model=list[FormSchema])
async def get_forms_by_creator(
    creator_id: UUID,
    skip: int = 0,
    limit: int = 10,
    handler: GetFormsByCreatorHandler = Depends(get_forms_by_creator_handler)
):
    """Get all forms created by a specific creator (admin only)"""
    use_case_request = GetFormsByCreatorRequest(creator_id=creator_id, skip=skip, limit=limit)
    response = await handler.handle(use_case_request)
    return response.forms


@router.put("/forms/{form_id}", response_model=FormSchema)
async def update_form(
    form_id: UUID,
    request: UpdateFormAPIRequest,
    handler: UpdateFormHandler = Depends(get_update_form_handler)
):
    """Update a form"""
    try:
        use_case_request = UpdateFormRequest(
            form_id=form_id,
            title=request.title,
            description=request.description,
            fields=request.fields
        )
        response = await handler.handle(use_case_request)
        return response.form
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/forms/{form_id}")
async def delete_form(
    form_id: UUID,
    handler: DeleteFormHandler = Depends(get_delete_form_handler)
):
    """Delete a form"""
    try:
        use_case_request = DeleteFormRequest(form_id=form_id)
        response = await handler.handle(use_case_request)
        return {"success": response.success}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/files/{file_id}/view")
async def view_file(
    file_id: UUID,
    file_repository: FileRepository = Depends(get_file_repository)
):
    """View/download a file by ID. Supports inline viewing for PDFs, images, text files."""
    file_record = await file_repository.get_by_id(file_id)
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Download file from Azure Blob Storage
        blob_name = str(file_record.blob_name)
        file_content = await azure_storage_client.download_file(blob_name)
        
        # Determine content type
        content_type = str(file_record.content_type) if file_record.content_type is not None else "application/octet-stream"
        
        # For viewable files, use inline disposition; for others, use attachment
        viewable_types = [
            "application/pdf",
            "image/",
            "text/",
            "application/json",
        ]
        is_viewable = any(content_type.startswith(t) for t in viewable_types)
        
        disposition = "inline" if is_viewable else "attachment"
        
        return Response(
            content=file_content,
            media_type=content_type,
            headers={
                "Content-Disposition": f'{disposition}; filename="{file_record.original_filename}"',
            }
        )
    except Exception as e:
        logger.error(f"Error downloading file {file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")

