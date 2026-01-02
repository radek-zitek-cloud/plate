"""
Additional test fixtures and utilities.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.schemas.user import UserCreate
from app.core.config import settings


# Test data factories
def user_data_factory(
    email: str = "test@example.com",
    username: str = "testuser",
    password: str = "TestPassword123",  # Updated to meet validation requirements
    is_active: bool = True,
    is_superuser: bool = False,
) -> dict:
    """Factory for creating user test data."""
    return {
        "email": email,
        "username": username,
        "password": password,
        "is_active": is_active,
        "is_superuser": is_superuser,
    }


# Helper functions for creating test users
async def create_test_user(
    db: AsyncSession,
    email: str = "test@example.com",
    username: str = "testuser",
    password: str = "TestPassword123",  # Updated to meet validation requirements
    is_active: bool = True,
    is_superuser: bool = False,
):
    """Helper to create a test user."""
    user_in = UserCreate(
        email=email,
        username=username,
        password=password,
        is_active=is_active,
        is_superuser=is_superuser,
    )
    return await crud.user.create(db, obj_in=user_in)


async def get_user_token(client: AsyncClient, email: str, password: str) -> str:
    """Helper to get authentication token for a user."""
    response = await client.post(
        f"{settings.API_V1_PREFIX}/auth/login",
        data={
            "username": email,  # OAuth2 uses 'username' field
            "password": password,
        },
    )
    return response.json()["access_token"]


# Additional reusable fixtures
@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user for use in tests."""
    return await create_test_user(
        db_session,
        email="testuser@example.com",
        username="testuser",
        password="testpassword123",
    )


@pytest.fixture
async def test_superuser(db_session: AsyncSession):
    """Create a test superuser for use in tests."""
    return await create_test_user(
        db_session,
        email="testsuperuser@example.com",
        username="testsuperuser",
        password="testpassword123",
        is_superuser=True,
    )


@pytest.fixture
async def inactive_user(db_session: AsyncSession):
    """Create an inactive test user."""
    return await create_test_user(
        db_session,
        email="inactive@example.com",
        username="inactiveuser",
        password="testpassword123",
        is_active=False,
    )


@pytest.fixture
async def test_user_token(client: AsyncClient, test_user) -> str:
    """Get authentication token for test user."""
    return await get_user_token(
        client, email="testuser@example.com", password="testpassword123"
    )


@pytest.fixture
async def test_superuser_token(client: AsyncClient, test_superuser) -> str:
    """Get authentication token for test superuser."""
    return await get_user_token(
        client, email="testsuperuser@example.com", password="testpassword123"
    )


@pytest.fixture
async def multiple_users(db_session: AsyncSession):
    """Create multiple users for testing list/pagination endpoints."""
    users = []
    for i in range(10):
        user = await create_test_user(
            db_session,
            email=f"user{i}@example.com",
            username=f"user{i}",
            password="testpassword123",
        )
        users.append(user)
    return users


# Test assertion helpers
def assert_user_response(data: dict, expected_email: str, expected_username: str):
    """Helper to assert user response has expected format and values."""
    assert "id" in data
    assert data["email"] == expected_email
    assert data["username"] == expected_username
    assert "password" not in data
    assert "hashed_password" not in data
    assert "created_at" in data
    assert "updated_at" in data
    assert "is_active" in data
    assert "is_superuser" in data


def assert_token_response(data: dict):
    """Helper to assert token response has expected format."""
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0


def assert_error_response(data: dict, expected_status: int):
    """Helper to assert error response has expected format."""
    assert "detail" in data
    assert isinstance(data["detail"], str)


# Test data generators
class UserTestData:
    """Collection of test user data."""

    VALID_USER = {
        "email": "valid@example.com",
        "username": "validuser",
        "password": "validpassword123",
    }

    VALID_SUPERUSER = {
        "email": "admin@example.com",
        "username": "adminuser",
        "password": "adminpassword123",
        "is_superuser": True,
    }

    INVALID_EMAIL = {
        "email": "not-an-email",
        "username": "testuser",
        "password": "password123",
    }

    MISSING_PASSWORD = {"email": "test@example.com", "username": "testuser"}

    MISSING_EMAIL = {"username": "testuser", "password": "password123"}

    MISSING_USERNAME = {"email": "test@example.com", "password": "password123"}


# Parametrized test data
VALID_PASSWORDS = [
    "simple123",
    "Complex@Pass123!",
    "super-long-password-with-many-characters-1234567890",
    "пароль123",  # Unicode
    "🔐🔑password",  # Emoji
    "p@$$w0rd!#$%^&*()",  # Special chars
]

INVALID_EMAILS = [
    "notanemail",
    "@example.com",
    "test@",
    "test @example.com",  # Space
    "",  # Empty
]

VALID_EMAILS = [
    "test@example.com",
    "user.name@example.com",
    "user+tag@example.co.uk",
    "123@example.com",
]
