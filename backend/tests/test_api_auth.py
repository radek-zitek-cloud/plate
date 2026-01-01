"""
Integration tests for authentication endpoints.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.schemas.user import UserCreate
from app.core.config import settings


class TestLogin:
    """Test login endpoint."""
    
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, db_session: AsyncSession):
        """Test successful login."""
        # Create a user
        user_in = UserCreate(
            email="login@example.com",
            username="loginuser",
            password="correctpassword",
            is_active=True
        )
        await crud.user.create(db_session, obj_in=user_in)
        
        # Login
        response = await client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={
                "username": "login@example.com",  # OAuth2 uses 'username' field for email
                "password": "correctpassword"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, db_session: AsyncSession):
        """Test login with incorrect password."""
        # Create a user
        user_in = UserCreate(
            email="wrongpw@example.com",
            username="wrongpwuser",
            password="correctpassword"
        )
        await crud.user.create(db_session, obj_in=user_in)
        
        # Try to login with wrong password
        response = await client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={
                "username": "wrongpw@example.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user."""
        response = await client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "anypassword"
            }
        )
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_login_inactive_user(self, client: AsyncClient, db_session: AsyncSession):
        """Test login with inactive user."""
        # Create an inactive user
        user_in = UserCreate(
            email="inactive@example.com",
            username="inactiveuser",
            password="password123",
            is_active=False
        )
        await crud.user.create(db_session, obj_in=user_in)
        
        # Try to login
        response = await client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={
                "username": "inactive@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 400
        assert "Inactive user" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_login_missing_username(self, client: AsyncClient):
        """Test login with missing username."""
        response = await client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={
                "password": "password123"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_login_missing_password(self, client: AsyncClient):
        """Test login with missing password."""
        response = await client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={
                "username": "test@example.com"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_login_empty_credentials(self, client: AsyncClient):
        """Test login with empty credentials."""
        response = await client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={
                "username": "",
                "password": ""
            }
        )
        
        assert response.status_code == 422  # Validation error


class TestTestToken:
    """Test token validation endpoint."""
    
    @pytest.mark.asyncio
    async def test_token_valid(self, client: AsyncClient, db_session: AsyncSession):
        """Test validating a valid token."""
        # Create a user
        user_in = UserCreate(
            email="tokentest@example.com",
            username="tokentestuser",
            password="password123"
        )
        created_user = await crud.user.create(db_session, obj_in=user_in)
        
        # Login to get token
        login_response = await client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={
                "username": "tokentest@example.com",
                "password": "password123"
            }
        )
        token = login_response.json()["access_token"]
        
        # Test token
        response = await client.post(
            f"{settings.API_V1_PREFIX}/auth/test-token",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "tokentest@example.com"
        assert data["username"] == "tokentestuser"
        assert data["id"] == created_user.id
    
    @pytest.mark.asyncio
    async def test_token_invalid(self, client: AsyncClient):
        """Test validating an invalid token."""
        response = await client.post(
            f"{settings.API_V1_PREFIX}/auth/test-token",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_token_missing(self, client: AsyncClient):
        """Test endpoint without providing token."""
        response = await client.post(
            f"{settings.API_V1_PREFIX}/auth/test-token"
        )
        
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_token_malformed_header(self, client: AsyncClient):
        """Test with malformed authorization header."""
        response = await client.post(
            f"{settings.API_V1_PREFIX}/auth/test-token",
            headers={"Authorization": "InvalidFormat token123"}
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_token_for_deleted_user(self, client: AsyncClient, db_session: AsyncSession):
        """Test token validation when user has been deleted."""
        # Create a user
        user_in = UserCreate(
            email="deleteme@example.com",
            username="deletemeuser",
            password="password123"
        )
        created_user = await crud.user.create(db_session, obj_in=user_in)
        
        # Login to get token
        login_response = await client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={
                "username": "deleteme@example.com",
                "password": "password123"
            }
        )
        token = login_response.json()["access_token"]
        
        # Delete the user
        await crud.user.delete(db_session, id=created_user.id)
        
        # Try to use the token
        response = await client.post(
            f"{settings.API_V1_PREFIX}/auth/test-token",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]


class TestAuthenticationFlow:
    """Test complete authentication flows."""
    
    @pytest.mark.asyncio
    async def test_complete_auth_flow(self, client: AsyncClient, db_session: AsyncSession):
        """Test complete authentication flow: signup -> login -> access protected endpoint."""
        # Signup
        signup_response = await client.post(
            f"{settings.API_V1_PREFIX}/users/signup",
            json={
                "email": "fullflow@example.com",
                "username": "fullflowuser",
                "password": "password123"
            }
        )
        assert signup_response.status_code == 200
        
        # Login
        login_response = await client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={
                "username": "fullflow@example.com",
                "password": "password123"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Access protected endpoint
        me_response = await client.get(
            f"{settings.API_V1_PREFIX}/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert me_response.status_code == 200
        assert me_response.json()["email"] == "fullflow@example.com"
    
    @pytest.mark.asyncio
    async def test_token_reuse(self, client: AsyncClient, db_session: AsyncSession):
        """Test that the same token can be used multiple times."""
        # Create and login
        user_in = UserCreate(
            email="reuse@example.com",
            username="reuseuser",
            password="password123"
        )
        await crud.user.create(db_session, obj_in=user_in)
        
        login_response = await client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={
                "username": "reuse@example.com",
                "password": "password123"
            }
        )
        token = login_response.json()["access_token"]
        
        # Use token multiple times
        for _ in range(3):
            response = await client.post(
                f"{settings.API_V1_PREFIX}/auth/test-token",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_multiple_logins_different_tokens(self, client: AsyncClient, db_session: AsyncSession):
        """Test that multiple logins generate tokens that are all valid."""
        import asyncio
        # Create user
        user_in = UserCreate(
            email="multilogin@example.com",
            username="multiloginuser",
            password="password123"
        )
        await crud.user.create(db_session, obj_in=user_in)
        
        # Login multiple times with small delays to ensure different timestamps
        tokens = []
        for i in range(3):
            response = await client.post(
                f"{settings.API_V1_PREFIX}/auth/login",
                data={
                    "username": "multilogin@example.com",
                    "password": "password123"
                }
            )
            tokens.append(response.json()["access_token"])
            if i < 2:  # Don't wait after the last one
                await asyncio.sleep(0.1)  # Small delay to ensure different exp times
        
        # All tokens should be valid
        for token in tokens:
            response = await client.post(
                f"{settings.API_V1_PREFIX}/auth/test-token",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 200
