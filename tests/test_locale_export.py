import pytest
from uuid import uuid4
from app.domain.models import User, Form, FormField, FormSubmission


@pytest.mark.asyncio
async def test_export_with_valid_locale_en(client, db_session, mock_azure_storage):
    """Test export with valid English locale"""
    # Create admin user
    admin = User(
        id=uuid4(),
        name="Admin",
        email="admin@test.com",
        is_admin=True,
    )
    db_session.add(admin)
    
    # Create form
    form = Form(
        id=uuid4(),
        title="Test Form",
        description="Test Description",
        creator_id=admin.id,
    )
    db_session.add(form)
    
    # Create form field
    field = FormField(
        id=uuid4(),
        form_id=form.id,
        field_type="text",
        label="Name",
        name="name",
        is_required=True,
        order=0,
    )
    db_session.add(field)
    
    # Create submission
    submission = FormSubmission(
        id=uuid4(),
        form_id=form.id,
        user_id=admin.id,
    )
    db_session.add(submission)
    await db_session.commit()
    
    # Test export with locale=en
    response = await client.get(
        f"/api/v1/submissions/{submission.id}/export?format=csv&locale=en"
    )
    
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_export_with_valid_locale_uk(client, db_session, mock_azure_storage):
    """Test export with valid Ukrainian locale"""
    # Create admin user
    admin = User(
        id=uuid4(),
        name="Admin",
        email="admin@test.com",
        is_admin=True,
    )
    db_session.add(admin)
    
    # Create form
    form = Form(
        id=uuid4(),
        title="Test Form",
        description="Test Description",
        creator_id=admin.id,
    )
    db_session.add(form)
    
    # Create form field
    field = FormField(
        id=uuid4(),
        form_id=form.id,
        field_type="text",
        label="Name",
        name="name",
        is_required=True,
        order=0,
    )
    db_session.add(field)
    
    # Create submission
    submission = FormSubmission(
        id=uuid4(),
        form_id=form.id,
        user_id=admin.id,
    )
    db_session.add(submission)
    await db_session.commit()
    
    # Test export with locale=uk
    response = await client.get(
        f"/api/v1/submissions/{submission.id}/export?format=csv&locale=uk"
    )
    
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_export_with_invalid_locale_fallback_to_en(client, db_session, mock_azure_storage):
    """Test export with invalid locale (ru) should fallback to English"""
    # Create admin user
    admin = User(
        id=uuid4(),
        name="Admin",
        email="admin@test.com",
        is_admin=True,
    )
    db_session.add(admin)
    
    # Create form
    form = Form(
        id=uuid4(),
        title="Test Form",
        description="Test Description",
        creator_id=admin.id,
    )
    db_session.add(form)
    
    # Create form field
    field = FormField(
        id=uuid4(),
        form_id=form.id,
        field_type="text",
        label="Name",
        name="name",
        is_required=True,
        order=0,
    )
    db_session.add(field)
    
    # Create submission
    submission = FormSubmission(
        id=uuid4(),
        form_id=form.id,
        user_id=admin.id,
    )
    db_session.add(submission)
    await db_session.commit()
    
    # Test export with invalid locale=ru (should fallback to en without 422 error)
    response = await client.get(
        f"/api/v1/submissions/{submission.id}/export?format=csv&locale=ru"
    )
    
    # Should NOT return 422 validation error
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_export_with_random_locale_fallback(client, db_session, mock_azure_storage):
    """Test export with completely random locale should fallback to English"""
    # Create admin user
    admin = User(
        id=uuid4(),
        name="Admin",
        email="admin@test.com",
        is_admin=True,
    )
    db_session.add(admin)
    
    # Create form
    form = Form(
        id=uuid4(),
        title="Test Form",
        description="Test Description",
        creator_id=admin.id,
    )
    db_session.add(form)
    
    # Create form field
    field = FormField(
        id=uuid4(),
        form_id=form.id,
        field_type="text",
        label="Name",
        name="name",
        is_required=True,
        order=0,
    )
    db_session.add(field)
    
    # Create submission
    submission = FormSubmission(
        id=uuid4(),
        form_id=form.id,
        user_id=admin.id,
    )
    db_session.add(submission)
    await db_session.commit()
    
    # Test export with random locale (should fallback to en without error)
    response = await client.get(
        f"/api/v1/submissions/{submission.id}/export?format=csv&locale=xyz123"
    )
    
    # Should NOT return 422 validation error
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_export_xlsx_with_invalid_locale(client, db_session, mock_azure_storage):
    """Test XLSX export with invalid locale should also work"""
    # Create admin user
    admin = User(
        id=uuid4(),
        name="Admin",
        email="admin@test.com",
        is_admin=True,
    )
    db_session.add(admin)
    
    # Create form
    form = Form(
        id=uuid4(),
        title="Test Form",
        description="Test Description",
        creator_id=admin.id,
    )
    db_session.add(form)
    
    # Create form field
    field = FormField(
        id=uuid4(),
        form_id=form.id,
        field_type="text",
        label="Name",
        name="name",
        is_required=True,
        order=0,
    )
    db_session.add(field)
    
    # Create submission
    submission = FormSubmission(
        id=uuid4(),
        form_id=form.id,
        user_id=admin.id,
    )
    db_session.add(submission)
    await db_session.commit()
    
    # Test XLSX export with invalid locale
    response = await client.get(
        f"/api/v1/submissions/{submission.id}/export?format=xlsx&locale=ru"
    )
    
    # Should NOT return 422 validation error
    assert response.status_code == 200
    assert "spreadsheetml.sheet" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_export_default_locale_when_not_provided(client, db_session, mock_azure_storage):
    """Test export without locale parameter should use default (en)"""
    # Create admin user
    admin = User(
        id=uuid4(),
        name="Admin",
        email="admin@test.com",
        is_admin=True,
    )
    db_session.add(admin)
    
    # Create form
    form = Form(
        id=uuid4(),
        title="Test Form",
        description="Test Description",
        creator_id=admin.id,
    )
    db_session.add(form)
    
    # Create form field
    field = FormField(
        id=uuid4(),
        form_id=form.id,
        field_type="text",
        label="Name",
        name="name",
        is_required=True,
        order=0,
    )
    db_session.add(field)
    
    # Create submission
    submission = FormSubmission(
        id=uuid4(),
        form_id=form.id,
        user_id=admin.id,
    )
    db_session.add(submission)
    await db_session.commit()
    
    # Test export without locale parameter
    response = await client.get(
        f"/api/v1/submissions/{submission.id}/export?format=csv"
    )
    
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
