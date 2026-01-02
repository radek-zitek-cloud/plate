"""
Unit tests for User CRUD operations.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import verify_password


class TestCRUDUser:
    """Test CRUD operations for User model."""

    @pytest.mark.asyncio
    async def test_create_user(self, db_session: AsyncSession):
        """Test creating a new user."""
        user_in = UserCreate(
            email="test@example.com",
            username="testuser",
            password="TestPassword123",
            is_active=True,
            is_superuser=False,
        )

        user = await crud.user.create(db_session, obj_in=user_in)

        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.is_active is True
        assert user.is_superuser is False
        assert hasattr(user, "id")
        assert hasattr(user, "hashed_password")
        assert user.hashed_password != "TestPassword123"  # Should be hashed
        assert verify_password("TestPassword123", user.hashed_password)

    @pytest.mark.asyncio
    async def test_get_user(self, db_session: AsyncSession):
        """Test retrieving a user by ID."""
        # Create a user first
        user_in = UserCreate(
            email="get@example.com", username="getuser", password="Password123"
        )
        created_user = await crud.user.create(db_session, obj_in=user_in)

        # Get the user
        retrieved_user = await crud.user.get(db_session, id=created_user.id)

        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == "get@example.com"
        assert retrieved_user.username == "getuser"

    @pytest.mark.asyncio
    async def test_get_nonexistent_user(self, db_session: AsyncSession):
        """Test retrieving a user that doesn't exist."""
        user = await crud.user.get(db_session, id=99999)
        assert user is None

    @pytest.mark.asyncio
    async def test_get_user_by_email(self, db_session: AsyncSession):
        """Test retrieving a user by email."""
        user_in = UserCreate(
            email="email@example.com", username="emailuser", password="Password123"
        )
        created_user = await crud.user.create(db_session, obj_in=user_in)

        retrieved_user = await crud.user.get_by_email(
            db_session, email="email@example.com"
        )

        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == "email@example.com"

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, db_session: AsyncSession):
        """Test retrieving a user by email that doesn't exist."""
        user = await crud.user.get_by_email(db_session, email="notfound@example.com")
        assert user is None

    @pytest.mark.asyncio
    async def test_get_user_by_username(self, db_session: AsyncSession):
        """Test retrieving a user by username."""
        user_in = UserCreate(
            email="username@example.com",
            username="uniqueusername",
            password="Password123",
        )
        created_user = await crud.user.create(db_session, obj_in=user_in)

        retrieved_user = await crud.user.get_by_username(
            db_session, username="uniqueusername"
        )

        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.username == "uniqueusername"

    @pytest.mark.asyncio
    async def test_get_user_by_username_not_found(self, db_session: AsyncSession):
        """Test retrieving a user by username that doesn't exist."""
        user = await crud.user.get_by_username(db_session, username="notfounduser")
        assert user is None

    @pytest.mark.asyncio
    async def test_update_user(self, db_session: AsyncSession):
        """Test updating a user."""
        # Create a user
        user_in = UserCreate(
            email="update@example.com", username="updateuser", password="OldPassword1"
        )
        user = await crud.user.create(db_session, obj_in=user_in)

        # Update the user
        user_update = UserUpdate(email="newemail@example.com", username="newusername")
        updated_user = await crud.user.update(
            db_session, db_obj=user, obj_in=user_update
        )

        assert updated_user.id == user.id
        assert updated_user.email == "newemail@example.com"
        assert updated_user.username == "newusername"

    @pytest.mark.asyncio
    async def test_update_user_password(self, db_session: AsyncSession):
        """Test updating a user's password."""
        # Create a user
        user_in = UserCreate(
            email="password@example.com",
            username="passworduser",
            password="OldPassword1",
        )
        user = await crud.user.create(db_session, obj_in=user_in)
        old_hashed_password = user.hashed_password

        # Update password
        user_update = UserUpdate(password="NewPassword123")
        updated_user = await crud.user.update(
            db_session, db_obj=user, obj_in=user_update
        )

        assert updated_user.hashed_password != old_hashed_password
        assert verify_password("NewPassword123", updated_user.hashed_password)
        assert not verify_password("OldPassword1", updated_user.hashed_password)

    @pytest.mark.asyncio
    async def test_update_user_partial(self, db_session: AsyncSession):
        """Test partial update of a user."""
        # Create a user
        user_in = UserCreate(
            email="partial@example.com", username="partialuser", password="Password123"
        )
        user = await crud.user.create(db_session, obj_in=user_in)

        # Update only username
        user_update = UserUpdate(username="newpartialuser")
        updated_user = await crud.user.update(
            db_session, db_obj=user, obj_in=user_update
        )

        assert updated_user.username == "newpartialuser"
        assert updated_user.email == "partial@example.com"  # Unchanged

    @pytest.mark.asyncio
    async def test_delete_user(self, db_session: AsyncSession):
        """Test deleting a user."""
        # Create a user
        user_in = UserCreate(
            email="delete@example.com", username="deleteuser", password="Password123"
        )
        user = await crud.user.create(db_session, obj_in=user_in)
        user_id = user.id

        # Delete the user
        deleted_user = await crud.user.delete(db_session, id=user_id)

        assert deleted_user.id == user_id

        # Verify user is deleted
        retrieved_user = await crud.user.get(db_session, id=user_id)
        assert retrieved_user is None

    @pytest.mark.asyncio
    async def test_get_multi_users(self, db_session: AsyncSession):
        """Test retrieving multiple users."""
        # Create multiple users
        for i in range(5):
            user_in = UserCreate(
                email=f"user{i}@example.com",
                username=f"user{i}",
                password="Password123",
            )
            await crud.user.create(db_session, obj_in=user_in)

        # Get multiple users
        users = await crud.user.get_multi(db_session, skip=0, limit=10)

        assert len(users) == 5

    @pytest.mark.asyncio
    async def test_get_multi_with_pagination(self, db_session: AsyncSession):
        """Test pagination when retrieving multiple users."""
        # Create multiple users
        for i in range(10):
            user_in = UserCreate(
                email=f"page{i}@example.com",
                username=f"page{i}",
                password="Password123",
            )
            await crud.user.create(db_session, obj_in=user_in)

        # Get first page
        page1 = await crud.user.get_multi(db_session, skip=0, limit=5)
        assert len(page1) == 5

        # Get second page
        page2 = await crud.user.get_multi(db_session, skip=5, limit=5)
        assert len(page2) == 5

        # Ensure pages are different
        page1_ids = {user.id for user in page1}
        page2_ids = {user.id for user in page2}
        assert page1_ids.isdisjoint(page2_ids)

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, db_session: AsyncSession):
        """Test successful user authentication."""
        # Create a user
        user_in = UserCreate(
            email="auth@example.com", username="authuser", password="CorrectPassword1"
        )
        await crud.user.create(db_session, obj_in=user_in)

        # Authenticate
        authenticated_user = await crud.user.authenticate(
            db_session, email="auth@example.com", password="CorrectPassword1"
        )

        assert authenticated_user is not None
        assert authenticated_user.email == "auth@example.com"

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, db_session: AsyncSession):
        """Test authentication with wrong password."""
        # Create a user
        user_in = UserCreate(
            email="wrongpw@example.com",
            username="wrongpwuser",
            password="CorrectPassword1",
        )
        await crud.user.create(db_session, obj_in=user_in)

        # Try to authenticate with wrong password
        authenticated_user = await crud.user.authenticate(
            db_session, email="wrongpw@example.com", password="WrongPassword1"
        )

        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_authenticate_user_nonexistent_email(self, db_session: AsyncSession):
        """Test authentication with non-existent email."""
        authenticated_user = await crud.user.authenticate(
            db_session, email="nonexistent@example.com", password="Password1"
        )

        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_is_active(self, db_session: AsyncSession):
        """Test checking if user is active."""
        # Create active user
        user_in = UserCreate(
            email="active@example.com",
            username="activeuser",
            password="Password123",
            is_active=True,
        )
        active_user = await crud.user.create(db_session, obj_in=user_in)

        assert await crud.user.is_active(active_user) is True

        # Create inactive user
        user_in = UserCreate(
            email="inactive@example.com",
            username="inactiveuser",
            password="Password123",
            is_active=False,
        )
        inactive_user = await crud.user.create(db_session, obj_in=user_in)

        assert await crud.user.is_active(inactive_user) is False

    @pytest.mark.asyncio
    async def test_is_superuser(self, db_session: AsyncSession):
        """Test checking if user is superuser."""
        # Create regular user
        user_in = UserCreate(
            email="regular@example.com",
            username="regularuser",
            password="Password123",
            is_superuser=False,
        )
        regular_user = await crud.user.create(db_session, obj_in=user_in)

        assert await crud.user.is_superuser(regular_user) is False

        # Create superuser
        user_in = UserCreate(
            email="super@example.com",
            username="superuser",
            password="Password123",
            is_superuser=True,
        )
        super_user = await crud.user.create(db_session, obj_in=user_in)

        assert await crud.user.is_superuser(super_user) is True
