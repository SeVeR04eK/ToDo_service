"""Tests for Authentication Router API endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.security import create_access_token, create_refresh_token
from tests.factories import UserFactory


@pytest.mark.integration
@pytest.mark.auth
class TestAuthRouter:
    """Test suite for Authentication API endpoints."""
    
    @pytest.mark.asyncio
    async def test_authentication_success(self, client: AsyncClient, db_session: AsyncSession, test_role):
        """Test successful authentication."""
        user = await UserFactory.create_in_db(
            db_session,
            username="testuser",
            password="TestPassword123!",
            role_id=test_role.id
        )
        
        response = await client.post(
            "/auth/authentication",
            data={
                "username": "testuser",
                "password": "TestPassword123!"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_authentication_wrong_username(self, client: AsyncClient):
        """Test authentication with wrong username."""
        response = await client.post(
            "/auth/authentication",
            data={
                "username": "wronguser",
                "password": "TestPassword123!"
            }
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_authentication_wrong_password(self, client: AsyncClient, db_session: AsyncSession, test_role):
        """Test authentication with wrong password."""
        await UserFactory.create_in_db(
            db_session,
            username="testuser",
            password="TestPassword123!",
            role_id=test_role.id
        )
        
        response = await client.post(
            "/auth/authentication",
            data={
                "username": "testuser",
                "password": "WrongPassword123!"
            }
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_authentication_missing_fields(self, client: AsyncClient):
        """Test authentication with missing fields."""
        response = await client.post(
            "/auth/authentication",
            data={"username": "testuser"}
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_refresh_token_success(self, client: AsyncClient, db_session: AsyncSession, test_user):
        """Test successful token refresh."""
        refresh_token = await create_refresh_token(
            username=test_user.username,
            user_id=test_user.id,
            session=db_session
        )
        
        response = await client.post(
            "/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
    
    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, client: AsyncClient):
        """Test refresh with invalid token."""
        response = await client.post(
            "/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_refresh_token_missing(self, client: AsyncClient):
        """Test refresh with missing token."""
        response = await client.post("/auth/refresh", json={})
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_access_token_can_be_used(self, client: AsyncClient, db_session: AsyncSession, test_user):
        """Test that access token works for authenticated requests."""
        access_token = create_access_token(
            username=test_user.username,
            user_id=test_user.id,
            role=test_user.role.name
        )
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.get("/tasks/me", headers=headers)
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_access_token_invalid(self, client: AsyncClient):
        """Test that invalid access token is rejected."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get("/tasks/me", headers=headers)
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_access_token_missing(self, client: AsyncClient):
        """Test that missing access token is rejected."""
        response = await client.get("/tasks/me")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_access_token_malformed(self, client: AsyncClient):
        """Test that malformed access token is rejected."""
        headers = {"Authorization": "InvalidFormat token"}
        response = await client.get("/tasks/me", headers=headers)
        
        assert response.status_code == 401
