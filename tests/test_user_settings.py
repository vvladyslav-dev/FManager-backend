import io
import pytest
from httpx import AsyncClient
from app.app import main  # adjust if main app import differs


@pytest.mark.asyncio
async def test_change_password_success(test_app_client: AsyncClient, create_user_with_password):
    user, token = await create_user_with_password(password="oldpass123")
    # Auth header
    headers = {"Authorization": f"Bearer {token}"}
    # Change password
    resp = await test_app_client.post(
        "/auth/change-password",
        json={"old_password": "oldpass123", "new_password": "newpass456"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["success"] is True


@pytest.mark.asyncio
async def test_change_password_invalid_current(test_app_client: AsyncClient, create_user_with_password):
    user, token = await create_user_with_password(password="oldpass123")
    headers = {"Authorization": f"Bearer {token}"}
    resp = await test_app_client.post(
        "/auth/change-password",
        json={"old_password": "wrong", "new_password": "newpass456"},
        headers=headers,
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_upload_avatar_success(test_app_client: AsyncClient, create_user_with_password):
    user, token = await create_user_with_password(password="secret")
    headers = {"Authorization": f"Bearer {token}"}
    # Prepare a small PNG file in memory
    content = b"\x89PNG\r\n\x1a\n" + b"0" * 128
    files = {"file": ("avatar.png", io.BytesIO(content), "image/png")}
    resp = await test_app_client.post(f"/users/{user.id}/avatar", files=files, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "avatar_url" in data


@pytest.mark.asyncio
async def test_upload_avatar_large_file(test_app_client: AsyncClient, create_user_with_password):
    user, token = await create_user_with_password(password="secret")
    headers = {"Authorization": f"Bearer {token}"}
    content = b"0" * (2 * 1024 * 1024 + 1)  # just over 2MB
    files = {"file": ("big.png", io.BytesIO(content), "image/png")}
    resp = await test_app_client.post(f"/users/{user.id}/avatar", files=files, headers=headers)
    assert resp.status_code == 400
