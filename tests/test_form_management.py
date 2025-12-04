import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_admin_registration_and_login(client):
    """Test admin registration and login flow."""
    
    # Register admin
    register_data = {
        "email": "newadmin@test.com",
        "name": "New Admin",
        "password": "password123"
    }
    
    register_response = await client.post("/api/v1/auth/register", json=register_data)
    assert register_response.status_code == 200
    register_result = register_response.json()
    assert "access_token" in register_result
    
    # Login with same credentials
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": register_data["email"],
            "password": register_data["password"]
        }
    )
    assert login_response.status_code == 200
    login_result = login_response.json()
    assert "access_token" in login_result
    # Tokens will be different due to different generation times, just verify both exist


@pytest.mark.asyncio
async def test_create_and_get_form(client, admin_user, auth_token):
    """Test creating and retrieving a form."""
    
    form_data = {
        "title": "My Test Form",
        "description": "A test form",
        "creator_id": str(admin_user.id),
        "fields": [
            {
                "field_type": "text",
                "label": "Name",
                "name": "name",
                "is_required": True,
                "order": 0
            }
        ]
    }
    
    # Create form
    create_response = await client.post(
        "/api/v1/forms",
        json=form_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert create_response.status_code == 200
    created_form = create_response.json()["form"]
    form_id = created_form["id"]
    
    # Get form by ID (public endpoint)
    get_response = await client.get(f"/api/v1/forms/{form_id}")
    assert get_response.status_code == 200
    form = get_response.json()["form"]
    assert form["id"] == form_id
    assert form["title"] == "My Test Form"
    assert len(form["fields"]) == 1
    
    # Get forms by creator
    creator_forms_response = await client.get(
        f"/api/v1/admin/{admin_user.id}/forms",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert creator_forms_response.status_code == 200
    forms = creator_forms_response.json()["forms"]
    assert len(forms) == 1
    assert forms[0]["id"] == form_id


@pytest.mark.asyncio
async def test_update_and_delete_form(client, admin_user, auth_token):
    """Test updating and deleting a form."""
    
    # Create form
    form_data = {
        "title": "Form to Update",
        "description": "Original description",
        "creator_id": str(admin_user.id),
        "fields": [
            {
                "field_type": "text",
                "label": "Field 1",
                "name": "field1",
                "is_required": True,
                "order": 0
            }
        ]
    }
    
    create_response = await client.post(
        "/api/v1/forms",
        json=form_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    form_id = create_response.json()["form"]["id"]
    
    # Update form
    update_data = {
        "form_id": form_id,
        "title": "Updated Form Title",
        "description": "Updated description",
        "fields": [
            {
                "field_type": "text",
                "label": "Updated Field",
                "name": "updated_field",
                "is_required": False,
                "order": 0
            }
        ]
    }
    
    update_response = await client.put(
        f"/api/v1/forms/{form_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert update_response.status_code == 200
    updated_form = update_response.json()["form"]
    assert updated_form["title"] == "Updated Form Title"
    assert len(updated_form["fields"]) == 1
    assert updated_form["fields"][0]["label"] == "Updated Field"
    
    # Delete form
    delete_response = await client.delete(
        f"/api/v1/forms/{form_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert delete_response.status_code == 200
    
    # Verify form is deleted
    get_response = await client.get(f"/api/v1/forms/{form_id}")
    assert get_response.status_code == 200
    assert get_response.json()["form"] is None

