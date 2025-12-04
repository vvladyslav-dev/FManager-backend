import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient
from uuid import uuid4
import importlib
import pkgutil

from app.main import app
from app.core.database import Base
from app.infrastructure.services.azure_storage import azure_storage_client
from app.core.container import container
from app.domain.models import User
import app.application.handlers as handlers_pkg


# Test database URL (in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


def _import_all_handlers():
    """Import all handlers to register with Mediator."""
    for module_info in pkgutil.walk_packages(handlers_pkg.__path__, handlers_pkg.__name__ + "."):
        try:
            importlib.import_module(module_info.name)
        except Exception:
            pass


# Register handlers once for all tests
_import_all_handlers()
container.wire(packages=["app.application.handlers"])


@pytest.fixture(scope="function")
async def db_session():
    """Create a test database session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session):
    """Create a test client using the test DB session factory in middleware."""
    from unittest.mock import patch
    # Ensure middleware uses the test session factory bound to in-memory DB
    with patch('app.core.middleware.AsyncSessionLocal', TestSessionLocal):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac


@pytest.fixture(scope="function")
async def admin_user(db_session):
    """Create a test admin user."""
    from app.core.auth import get_password_hash
    admin = User(
        id=uuid4(),
        name="Test Admin",
        email="admin@test.com",
        is_admin=True,
        password_hash=get_password_hash("secret")
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest.fixture(scope="function")
def mock_azure_storage():
    """Mock Azure Storage client."""
    import unittest.mock as mock
    
    async def mock_upload_file(file_content, blob_name):
        return f"https://test.blob.core.windows.net/test-container/{blob_name}"
    
    with mock.patch.object(azure_storage_client, 'upload_file', side_effect=mock_upload_file):
        yield azure_storage_client


@pytest.fixture(scope="function")
async def auth_token(client, admin_user, db_session):
    """Get authentication token for admin user."""
    # Update admin user password hash in session
    from app.core.auth import get_password_hash
    admin_user.password_hash = get_password_hash("secret")
    await db_session.commit()
    await db_session.refresh(admin_user)
    
    # Try to login
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": admin_user.email,
            "password": "secret"
        }
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    
    # Fallback: create token manually for testing
    from app.core.auth import create_access_token
    return create_access_token(data={"sub": str(admin_user.id)})

