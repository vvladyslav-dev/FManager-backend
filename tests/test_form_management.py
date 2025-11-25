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
    assert login_result["access_token"] == register_result["access_token"]


@pytest.mark.asyncio
async def test_create_and_get_form(client, admin_user, auth_token):
    """Test creating and retrieving a form."""
    
    form_data = {
        "title": "My Test Form",
        "description": "A test form",
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
        f"/api/v1/forms?creator_id={admin_user.id}",
        json=form_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert create_response.status_code == 200
    created_form = create_response.json()
    form_id = created_form["id"]
    
    # Get form by ID (public endpoint)
    get_response = await client.get(f"/api/v1/forms/{form_id}")
    assert get_response.status_code == 200
    form = get_response.json()
    assert form["id"] == form_id
    assert form["title"] == "My Test Form"
    assert len(form["fields"]) == 1
    
    # Get forms by creator
    creator_forms_response = await client.get(
        f"/api/v1/admin/{admin_user.id}/forms",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert creator_forms_response.status_code == 200
    forms = creator_forms_response.json()
    assert len(forms) == 1
    assert forms[0]["id"] == form_id


@pytest.mark.asyncio
async def test_update_and_delete_form(client, admin_user, auth_token):
    """Test updating and deleting a form."""
    
    # Create form
    form_data = {
        "title": "Form to Update",
        "description": "Original description",
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
        f"/api/v1/forms?creator_id={admin_user.id}",
        json=form_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    form_id = create_response.json()["id"]
    
    # Update form
    update_data = {
        "title": "Updated Form Title",
        "description": "Updated description",
        "is_active": False,
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
    updated_form = update_response.json()
    assert updated_form["title"] == "Updated Form Title"
    assert updated_form["is_active"] is False
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
    assert get_response.status_code == 404

