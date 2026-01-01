"""
Tests for API dependencies and dependency injection.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt

from app import crud
from app.schemas.user import UserCreate
from app.core.config import settings
from app.core.security import create_access_token


class TestDependencies:
    """Test FastAPI dependencies."""
    
    @pytest.mark.asyncio
    async def test_get_db_dependency(self, client: AsyncClient, db_session: AsyncSession):
        """Test that database dependency provides working session."""
        # This is implicitly tested by other tests, but we can verify it works
        user_in = UserCreate(
            email="dbtest@example.com",
            username="dbtestuser",
            password="password123"
        )
        user = await crud.user.create(db_session, obj_in=user_in)
        
        assert user.id is not None
        assert user.email == "dbtest@example.com"
    
    @pytest.mark.asyncio
    async def test_oauth2_scheme_extracts_token(self, client: AsyncClient, db_session: AsyncSession):
        """Test that OAuth2 scheme correctly extracts Bearer token."""
        # Create and login
        user_in = UserCreate(
            email="oauth@example.com",
            username="oauthuser",
            password="password123"
        )
        await crud.user.create(db_session, obj_in=user_in)
        
        login_response = await client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={
                "username": "oauth@example.com",
                "password": "password123"
            }
        )
        token = login_response.json()["access_token"]
        
        # Use token
        response = await client.get(
            f"{settings.API_V1_PREFIX}/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_get_current_user_dependency(self, client: AsyncClient, db_session: AsyncSession):
        """Test get_current_user dependency."""
        # Create user
        user_in = UserCreate(
            email="current@example.com",
            username="currentuser",
            password="password123"
        )
        created_user = await crud.user.create(db_session, obj_in=user_in)
        
        # Get token
        token = create_access_token(subject=str(created_user.id))
        
        # Use endpoint that depends on get_current_user
        response = await client.get(
            f"{settings.API_V1_PREFIX}/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["id"] == created_user.id
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """Test get_current_user with invalid token."""
        response = await client.get(
            f"{settings.API_V1_PREFIX}/users/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_get_current_user_token_for_nonexistent_user(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test get_current_user with token for deleted user."""
        # Create user
        user_in = UserCreate(
            email="deleted@example.com",
            username="deleteduser",
            password="password123"
        )
        user = await crud.user.create(db_session, obj_in=user_in)
        
        # Create token
        token = create_access_token(subject=str(user.id))
        
        # Delete user
        await crud.user.delete(db_session, id=user.id)
        
        # Try to use token
        response = await client.get(
            f"{settings.API_V1_PREFIX}/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_current_user_token_missing_subject(self, client: AsyncClient):
        """Test get_current_user with token missing subject claim."""
        # Create token without 'sub' claim
        token = jwt.encode(
            {"exp": 9999999999},  # Far future
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        response = await client.get(
            f"{settings.API_V1_PREFIX}/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_current_active_user_dependency(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test get_current_active_user dependency accepts active user."""
        # Create active user
        user_in = UserCreate(
            email="active@example.com",
            username="activeuser",
            password="password123",
            is_active=True
        )
        await crud.user.create(db_session, obj_in=user_in)
        
        # Login
        login_response = await client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={
                "username": "active@example.com",
                "password": "password123"
            }
        )
        token = login_response.json()["access_token"]
        
        # Access endpoint requiring active user
        response = await client.get(
            f"{settings.API_V1_PREFIX}/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_get_current_active_user_rejects_inactive(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test get_current_active_user dependency rejects inactive user."""
        # Create inactive user
        user_in = UserCreate(
            email="inactive@example.com",
            username="inactiveuser",
            password="password123",
            is_active=False
        )
        user = await crud.user.create(db_session, obj_in=user_in)
        
        # Create token manually (can't login with inactive user)
        token = create_access_token(subject=str(user.id))
        
        # Try to access endpoint
        response = await client.get(
            f"{settings.API_V1_PREFIX}/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        assert "Inactive user" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_get_current_superuser_dependency(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test get_current_superuser dependency accepts superuser."""
        # Create superuser
        user_in = UserCreate(
            email="super@example.com",
            username="superuser",
            password="password123",
            is_superuser=True
        )
        await crud.user.create(db_session, obj_in=user_in)
        
        # Login
        login_response = await client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={
                "username": "super@example.com",
                "password": "password123"
            }
        )
        token = login_response.json()["access_token"]
        
        # Access superuser endpoint
        response = await client.get(
            f"{settings.API_V1_PREFIX}/users/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_get_current_superuser_rejects_normal_user(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test get_current_superuser dependency rejects normal user."""
        # Create normal user
        user_in = UserCreate(
            email="normal@example.com",
            username="normaluser",
            password="password123",
            is_superuser=False
        )
        await crud.user.create(db_session, obj_in=user_in)
        
        # Login
        login_response = await client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={
                "username": "normal@example.com",
                "password": "password123"
            }
        )
        token = login_response.json()["access_token"]
        
        # Try to access superuser endpoint
        response = await client.get(
            f"{settings.API_V1_PREFIX}/users/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
        assert "enough privileges" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_dependency_chain_execution_order(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test that dependency chain executes in correct order."""
        # get_current_active_user depends on get_current_user
        # get_current_user depends on get_db and oauth2_scheme
        
        # Create user
        user_in = UserCreate(
            email="chain@example.com",
            username="chainuser",
            password="password123"
        )
        await crud.user.create(db_session, obj_in=user_in)
        
        # Login
        login_response = await client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={
                "username": "chain@example.com",
                "password": "password123"
            }
        )
        token = login_response.json()["access_token"]
        
        # Use endpoint with dependency chain
        response = await client.get(
            f"{settings.API_V1_PREFIX}/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # If we get here with 200, all dependencies executed correctly
        assert response.status_code == 200
        assert response.json()["email"] == "chain@example.com"
