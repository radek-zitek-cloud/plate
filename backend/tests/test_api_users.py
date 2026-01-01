"""
Integration tests for user endpoints.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.schemas.user import UserCreate
from app.core.config import settings


@pytest.fixture
async def normal_user_token(client: AsyncClient, db_session: AsyncSession) -> str:
    """Create a normal user and return their access token."""
    user_in = UserCreate(
        email="normaluser@example.com",
        username="normaluser",
        password="password123",
        is_active=True,
        is_superuser=False
    )
    await crud.user.create(db_session, obj_in=user_in)
    
    response = await client.post(
        f"{settings.API_V1_PREFIX}/auth/login",
        data={
            "username": "normaluser@example.com",
            "password": "password123"
        }
    )
    return response.json()["access_token"]


@pytest.fixture
async def superuser_token(client: AsyncClient, db_session: AsyncSession) -> str:
    """Create a superuser and return their access token."""
    user_in = UserCreate(
        email="superuser@example.com",
        username="superuser",
        password="password123",
        is_active=True,
        is_superuser=True
    )
    await crud.user.create(db_session, obj_in=user_in)
    
    response = await client.post(
        f"{settings.API_V1_PREFIX}/auth/login",
        data={
            "username": "superuser@example.com",
            "password": "password123"
        }
    )
    return response.json()["access_token"]


class TestUserSignup:
    """Test user signup endpoint."""
    
    @pytest.mark.asyncio
    async def test_signup_success(self, client: AsyncClient):
        """Test successful user signup."""
        response = await client.post(
            f"{settings.API_V1_PREFIX}/users/signup",
            json={
                "email": "newsignup@example.com",
                "username": "newsignupuser",
                "password": "password123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newsignup@example.com"
        assert data["username"] == "newsignupuser"
        assert "password" not in data
        assert "hashed_password" not in data
        assert data["is_active"] is True
        assert data["is_superuser"] is False
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_signup_duplicate_email(self, client: AsyncClient, db_session: AsyncSession):
        """Test signup with duplicate email."""
        # Create first user
        user_in = UserCreate(
            email="duplicate@example.com",
            username="firstuser",
            password="password123"
        )
        await crud.user.create(db_session, obj_in=user_in)
        
        # Try to signup with same email
        response = await client.post(
            f"{settings.API_V1_PREFIX}/users/signup",
            json={
                "email": "duplicate@example.com",
                "username": "seconduser",
                "password": "password123"
            }
        )
        
        assert response.status_code == 400
        assert "email already exists" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_signup_duplicate_username(self, client: AsyncClient, db_session: AsyncSession):
        """Test signup with duplicate username."""
        # Create first user
        user_in = UserCreate(
            email="first@example.com",
            username="duplicateuser",
            password="password123"
        )
        await crud.user.create(db_session, obj_in=user_in)
        
        # Try to signup with same username
        response = await client.post(
            f"{settings.API_V1_PREFIX}/users/signup",
            json={
                "email": "second@example.com",
                "username": "duplicateuser",
                "password": "password123"
            }
        )
        
        assert response.status_code == 400
        assert "username already exists" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_signup_invalid_email(self, client: AsyncClient):
        """Test signup with invalid email format."""
        response = await client.post(
            f"{settings.API_V1_PREFIX}/users/signup",
            json={
                "email": "notanemail",
                "username": "testuser",
                "password": "password123"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_signup_missing_fields(self, client: AsyncClient):
        """Test signup with missing required fields."""
        response = await client.post(
            f"{settings.API_V1_PREFIX}/users/signup",
            json={
                "email": "test@example.com"
                # Missing username and password
            }
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_signup_short_password(self, client: AsyncClient):
        """Test signup with very short password (should still work, no validation)."""
        response = await client.post(
            f"{settings.API_V1_PREFIX}/users/signup",
            json={
                "email": "shortpw@example.com",
                "username": "shortpwuser",
                "password": "12"
            }
        )
        
        # Current implementation has no password length validation
        # This test documents current behavior
        assert response.status_code == 200


class TestReadUserMe:
    """Test read current user endpoint."""
    
    @pytest.mark.asyncio
    async def test_read_user_me_success(self, client: AsyncClient, normal_user_token: str):
        """Test reading current user info."""
        response = await client.get(
            f"{settings.API_V1_PREFIX}/users/me",
            headers={"Authorization": f"Bearer {normal_user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "normaluser@example.com"
        assert data["username"] == "normaluser"
        assert "password" not in data
        assert "hashed_password" not in data
    
    @pytest.mark.asyncio
    async def test_read_user_me_unauthorized(self, client: AsyncClient):
        """Test reading current user without authentication."""
        response = await client.get(
            f"{settings.API_V1_PREFIX}/users/me"
        )
        
        assert response.status_code == 401


class TestUpdateUserMe:
    """Test update current user endpoint."""
    
    @pytest.mark.asyncio
    async def test_update_user_me_email(self, client: AsyncClient, normal_user_token: str):
        """Test updating current user's email."""
        response = await client.put(
            f"{settings.API_V1_PREFIX}/users/me",
            headers={"Authorization": f"Bearer {normal_user_token}"},
            json={
                "email": "newemail@example.com"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newemail@example.com"
    
    @pytest.mark.asyncio
    async def test_update_user_me_username(self, client: AsyncClient, normal_user_token: str):
        """Test updating current user's username."""
        response = await client.put(
            f"{settings.API_V1_PREFIX}/users/me",
            headers={"Authorization": f"Bearer {normal_user_token}"},
            json={
                "username": "newusername"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newusername"
    
    @pytest.mark.asyncio
    async def test_update_user_me_password(self, client: AsyncClient, db_session: AsyncSession):
        """Test updating current user's password."""
        # Create user and get token
        user_in = UserCreate(
            email="changepw@example.com",
            username="changepwuser",
            password="oldpassword"
        )
        await crud.user.create(db_session, obj_in=user_in)
        
        login_response = await client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={
                "username": "changepw@example.com",
                "password": "oldpassword"
            }
        )
        token = login_response.json()["access_token"]
        
        # Update password
        response = await client.put(
            f"{settings.API_V1_PREFIX}/users/me",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "password": "newpassword123"
            }
        )
        
        assert response.status_code == 200
        
        # Verify old password doesn't work
        old_login = await client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={
                "username": "changepw@example.com",
                "password": "oldpassword"
            }
        )
        assert old_login.status_code == 401
        
        # Verify new password works
        new_login = await client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={
                "username": "changepw@example.com",
                "password": "newpassword123"
            }
        )
        assert new_login.status_code == 200
    
    @pytest.mark.asyncio
    async def test_update_user_me_unauthorized(self, client: AsyncClient):
        """Test updating user without authentication."""
        response = await client.put(
            f"{settings.API_V1_PREFIX}/users/me",
            json={
                "email": "newemail@example.com"
            }
        )
        
        assert response.status_code == 401


class TestReadUserById:
    """Test read user by ID endpoint."""
    
    @pytest.mark.asyncio
    async def test_read_user_by_id_success(
        self, client: AsyncClient, db_session: AsyncSession, normal_user_token: str
    ):
        """Test reading another user by ID."""
        # Create another user
        user_in = UserCreate(
            email="otheruser@example.com",
            username="otheruser",
            password="password123"
        )
        other_user = await crud.user.create(db_session, obj_in=user_in)
        
        # Read that user
        response = await client.get(
            f"{settings.API_V1_PREFIX}/users/{other_user.id}",
            headers={"Authorization": f"Bearer {normal_user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "otheruser@example.com"
        assert data["id"] == other_user.id
    
    @pytest.mark.asyncio
    async def test_read_user_by_id_not_found(self, client: AsyncClient, normal_user_token: str):
        """Test reading non-existent user."""
        response = await client.get(
            f"{settings.API_V1_PREFIX}/users/99999",
            headers={"Authorization": f"Bearer {normal_user_token}"}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_read_user_by_id_unauthorized(self, client: AsyncClient, db_session: AsyncSession):
        """Test reading user without authentication."""
        # Create a user
        user_in = UserCreate(
            email="test@example.com",
            username="testuser",
            password="password123"
        )
        user = await crud.user.create(db_session, obj_in=user_in)
        
        response = await client.get(
            f"{settings.API_V1_PREFIX}/users/{user.id}"
        )
        
        assert response.status_code == 401


class TestReadUsers:
    """Test list users endpoint (admin only)."""
    
    @pytest.mark.asyncio
    async def test_read_users_as_superuser(
        self, client: AsyncClient, db_session: AsyncSession, superuser_token: str
    ):
        """Test listing users as superuser."""
        # Create some users
        for i in range(3):
            user_in = UserCreate(
                email=f"listuser{i}@example.com",
                username=f"listuser{i}",
                password="password123"
            )
            await crud.user.create(db_session, obj_in=user_in)
        
        response = await client.get(
            f"{settings.API_V1_PREFIX}/users/",
            headers={"Authorization": f"Bearer {superuser_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3  # At least the 3 we created
    
    @pytest.mark.asyncio
    async def test_read_users_with_pagination(
        self, client: AsyncClient, db_session: AsyncSession, superuser_token: str
    ):
        """Test listing users with pagination."""
        # Create multiple users
        for i in range(10):
            user_in = UserCreate(
                email=f"page{i}@example.com",
                username=f"page{i}",
                password="password123"
            )
            await crud.user.create(db_session, obj_in=user_in)
        
        # Get first page
        response = await client.get(
            f"{settings.API_V1_PREFIX}/users/?skip=0&limit=5",
            headers={"Authorization": f"Bearer {superuser_token}"}
        )
        
        assert response.status_code == 200
        assert len(response.json()) == 5
        
        # Get second page
        response = await client.get(
            f"{settings.API_V1_PREFIX}/users/?skip=5&limit=5",
            headers={"Authorization": f"Bearer {superuser_token}"}
        )
        
        assert response.status_code == 200
        assert len(response.json()) >= 5
    
    @pytest.mark.asyncio
    async def test_read_users_as_normal_user(self, client: AsyncClient, normal_user_token: str):
        """Test that normal users cannot list all users."""
        response = await client.get(
            f"{settings.API_V1_PREFIX}/users/",
            headers={"Authorization": f"Bearer {normal_user_token}"}
        )
        
        assert response.status_code == 403
        assert "enough privileges" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_read_users_unauthorized(self, client: AsyncClient):
        """Test listing users without authentication."""
        response = await client.get(
            f"{settings.API_V1_PREFIX}/users/"
        )
        
        assert response.status_code == 401


class TestDeleteUser:
    """Test delete user endpoint (admin only)."""
    
    @pytest.mark.asyncio
    async def test_delete_user_as_superuser(
        self, client: AsyncClient, db_session: AsyncSession, superuser_token: str
    ):
        """Test deleting a user as superuser."""
        # Create a user
        user_in = UserCreate(
            email="deleteme@example.com",
            username="deletemeuser",
            password="password123"
        )
        user = await crud.user.create(db_session, obj_in=user_in)
        
        # Delete the user
        response = await client.delete(
            f"{settings.API_V1_PREFIX}/users/{user.id}",
            headers={"Authorization": f"Bearer {superuser_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user.id
        
        # Verify user is deleted
        get_response = await client.get(
            f"{settings.API_V1_PREFIX}/users/{user.id}",
            headers={"Authorization": f"Bearer {superuser_token}"}
        )
        assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, client: AsyncClient, superuser_token: str):
        """Test deleting non-existent user."""
        response = await client.delete(
            f"{settings.API_V1_PREFIX}/users/99999",
            headers={"Authorization": f"Bearer {superuser_token}"}
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_user_as_normal_user(
        self, client: AsyncClient, db_session: AsyncSession, normal_user_token: str
    ):
        """Test that normal users cannot delete users."""
        # Create a user
        user_in = UserCreate(
            email="cantdelete@example.com",
            username="cantdeleteuser",
            password="password123"
        )
        user = await crud.user.create(db_session, obj_in=user_in)
        
        response = await client.delete(
            f"{settings.API_V1_PREFIX}/users/{user.id}",
            headers={"Authorization": f"Bearer {normal_user_token}"}
        )
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_delete_user_unauthorized(self, client: AsyncClient, db_session: AsyncSession):
        """Test deleting user without authentication."""
        # Create a user
        user_in = UserCreate(
            email="test@example.com",
            username="testuser",
            password="password123"
        )
        user = await crud.user.create(db_session, obj_in=user_in)
        
        response = await client.delete(
            f"{settings.API_V1_PREFIX}/users/{user.id}"
        )
        
        assert response.status_code == 401


class TestUserPermissions:
    """Test user permission scenarios."""
    
    @pytest.mark.asyncio
    async def test_inactive_user_cannot_access_protected_endpoints(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test that inactive users cannot access protected endpoints."""
        # Create inactive user
        user_in = UserCreate(
            email="inactive@example.com",
            username="inactiveuser",
            password="password123",
            is_active=False
        )
        await crud.user.create(db_session, obj_in=user_in)
        
        # Cannot login (caught at login)
        login_response = await client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={
                "username": "inactive@example.com",
                "password": "password123"
            }
        )
        assert login_response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_user_can_read_own_profile(self, client: AsyncClient, normal_user_token: str):
        """Test that users can read their own profile."""
        response = await client.get(
            f"{settings.API_V1_PREFIX}/users/me",
            headers={"Authorization": f"Bearer {normal_user_token}"}
        )
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_user_can_update_own_profile(self, client: AsyncClient, normal_user_token: str):
        """Test that users can update their own profile."""
        response = await client.put(
            f"{settings.API_V1_PREFIX}/users/me",
            headers={"Authorization": f"Bearer {normal_user_token}"},
            json={
                "username": "updatedusername"
            }
        )
        
        assert response.status_code == 200
        assert response.json()["username"] == "updatedusername"
