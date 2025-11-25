import pytest
from httpx import AsyncClient
from uuid import uuid4


@pytest.mark.asyncio
async def test_full_form_submission_process(client, admin_user, mock_azure_storage, auth_token):
    """Test the complete form submission process:
    1. Admin creates a form
    2. User submits form with files
    3. Admin views submissions
    """
    
    # Step 1: Admin creates a form
    form_data = {
        "title": "Test Form",
        "description": "Test Description",
        "fields": [
            {
                "field_type": "text",
                "label": "Name",
                "name": "name",
                "is_required": True,
                "order": 0
            },
            {
                "field_type": "file",
                "label": "Upload File",
                "name": "file",
                "is_required": True,
                "order": 1
            }
        ]
    }
    
    create_response = await client.post(
        f"/api/v1/forms?creator_id={admin_user.id}",
        json=form_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert create_response.status_code == 200
    created_form = create_response.json()
    form_id = created_form["id"]
    assert created_form["title"] == "Test Form"
    assert len(created_form["fields"]) == 2
    
    # Step 2: Get form to verify it's active
    get_form_response = await client.get(f"/api/v1/forms/{form_id}")
    assert get_form_response.status_code == 200
    form = get_form_response.json()
    assert form["is_active"] is True
    
    # Step 3: User submits form (public endpoint, no auth)
    # Get field IDs from form
    text_field_id = form["fields"][0]["id"]
    file_field_id = form["fields"][1]["id"]
    
    # Submit form with multipart/form-data
    import io
    test_file_content = b"test file content"
    
    submit_data = {
        "user_name": "Test User",
        "user_email": "user@test.com",
        "field_values": f'{{"{text_field_id}": "John Doe"}}',
        "file_fields": f'{{"0": "{file_field_id}"}}'
    }
    
    files = [
        ("files", ("test.txt", io.BytesIO(test_file_content), "text/plain"))
    ]
    
    submit_response = await client.post(
        f"/api/v1/forms/{form_id}/submit",
        data=submit_data,
        files=files
    )
    
    assert submit_response.status_code == 200
    submission = submit_response.json()
    assert submission["user"]["name"] == "Test User"
    assert submission["form"]["id"] == form_id
    assert len(submission["field_values"]) == 1
    assert len(submission["files"]) == 1
    
    # Step 4: Admin views submissions
    submissions_response = await client.get(
        f"/api/v1/admin/{admin_user.id}/submissions",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert submissions_response.status_code == 200
    submissions = submissions_response.json()
    assert len(submissions) == 1
    assert submissions[0]["id"] == submission["id"]
    assert submissions[0]["user"]["name"] == "Test User"
    assert len(submissions[0]["files"]) == 1


@pytest.mark.asyncio
async def test_form_with_only_text_fields(client, admin_user, auth_token):
    """Test form submission with only text fields (no files)."""
    
    # Create form with only text fields
    form_data = {
        "title": "Text Only Form",
        "description": "Form with text fields only",
        "fields": [
            {
                "field_type": "text",
                "label": "First Name",
                "name": "first_name",
                "is_required": True,
                "order": 0
            },
            {
                "field_type": "textarea",
                "label": "Comments",
                "name": "comments",
                "is_required": False,
                "order": 1
            }
        ]
    }
    
    create_response = await client.post(
        f"/api/v1/forms?creator_id={admin_user.id}",
        json=form_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert create_response.status_code == 200
    form_id = create_response.json()["id"]
    
    # Submit form
    get_form_response = await client.get(f"/api/v1/forms/{form_id}")
    form = get_form_response.json()
    
    text_field_id = form["fields"][0]["id"]
    textarea_field_id = form["fields"][1]["id"]
    
    submit_data = {
        "user_name": "Jane Doe",
        "user_email": "jane@test.com",
        "field_values": f'{{"{text_field_id}": "Jane", "{textarea_field_id}": "Some comments"}}'
    }
    
    submit_response = await client.post(
        f"/api/v1/forms/{form_id}/submit",
        data=submit_data
    )
    
    assert submit_response.status_code == 200
    submission = submit_response.json()
    assert len(submission["field_values"]) == 2
    assert len(submission["files"]) == 0


@pytest.mark.asyncio
async def test_form_with_only_file_field(client, admin_user, mock_azure_storage, auth_token):
    """Test form submission with only file field."""
    
    # Create form with only file field
    form_data = {
        "title": "File Only Form",
        "description": "Form with file field only",
        "fields": [
            {
                "field_type": "file",
                "label": "Upload Document",
                "name": "document",
                "is_required": True,
                "order": 0
            }
        ]
    }
    
    create_response = await client.post(
        f"/api/v1/forms?creator_id={admin_user.id}",
        json=form_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert create_response.status_code == 200
    form_id = create_response.json()["id"]
    
    # Submit form
    get_form_response = await client.get(f"/api/v1/forms/{form_id}")
    form = get_form_response.json()
    
    file_field_id = form["fields"][0]["id"]
    
    import io
    test_file_content = b"document content"
    
    submit_data = {
        "user_name": "File User",
        "field_values": "{}",  # Empty field_values
        "file_fields": f'{{"0": "{file_field_id}"}}'
    }
    
    files = [
        ("files", ("document.pdf", io.BytesIO(test_file_content), "application/pdf"))
    ]
    
    submit_response = await client.post(
        f"/api/v1/forms/{form_id}/submit",
        data=submit_data,
        files=files
    )
    
    assert submit_response.status_code == 200
    submission = submit_response.json()
    assert len(submission["field_values"]) == 0
    assert len(submission["files"]) == 1
    assert submission["files"][0]["original_filename"] == "document.pdf"

