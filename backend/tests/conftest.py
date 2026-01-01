import asyncio
import sys
from pathlib import Path
from typing import AsyncGenerator

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.core.database import Base
from app.main import app
from app.api.deps import get_db

# Use test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_password@localhost:5433/test_db"

# Create test engine with proper pool settings
test_engine = create_async_engine(
    TEST_DATABASE_URL, 
    echo=False,  # Disable SQL logging for cleaner test output
    poolclass=NullPool  # Use NullPool to avoid connection issues between tests
)
TestingSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the entire test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh database for each test function.
    
    This fixture creates all tables before the test runs,
    provides a database session to the test,
    then drops all tables after the test completes.
    
    This ensures each test starts with a clean database state.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create a test client with overridden database dependency.
    
    This fixture creates an HTTP client for testing your API endpoints.
    It overrides the get_db dependency to use the test database session
    instead of the production database.
    """
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()