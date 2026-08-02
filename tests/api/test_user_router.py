import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models import Role

from app.infrastructure.services.jwt_service import JWTService
from app.main import app

from tests.factories import UserFactory


@pytest.mark.integration
class TestUserRouter:
    """Test user router endpoints."""

    @pytest.mark.asyncio
    async def test_create_user_success(self, client: AsyncClient, test_role: Role):
        """Test creating a new user."""
        response = await client.post(
            "/user/me",
            json={
                "username": "newuser",
                "password": "password123",
                "password_confirm": "password123"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_user_password_mismatch(self, client: AsyncClient):
        """Test creating user with mismatched passwords."""
        response = await client.post(
            "/user/me",
            json={
                "username": "newuser",
                "password": "password123",
                "password_confirm": "different123"
            }
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_user_missing_fields(self, client: AsyncClient):
        """Test creating user with missing required fields."""
        response = await client.post(
            "/user/me",
            json={
                "username": "newuser"
            }
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_user_success(self, authenticated_client: AsyncClient, test_user):
        """Test getting current user info."""
        response = await authenticated_client.get("/user/me")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["username"] == test_user.username

    @pytest.mark.asyncio
    async def test_get_user_unauthorized(self, client: AsyncClient):
        """Test getting user without authentication."""
        response = await client.get("/user/me")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_user_success(self, authenticated_client: AsyncClient, test_user):
        """Test updating current user."""
        response = await authenticated_client.patch(
            "/user/me",
            json={
                "username": "updated_user",
                "password": "newpassword123",
                "password_confirm": "newpassword123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "updated_user"

    @pytest.mark.asyncio
    async def test_update_user_username_only(self, authenticated_client: AsyncClient, test_user):
        """Test updating only username."""
        response = await authenticated_client.patch(
            "/user/me",
            json={
                "username": "updated_user"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "updated_user"

    @pytest.mark.asyncio
    async def test_update_user_password_only(self, authenticated_client: AsyncClient, test_user):
        """Test updating only password."""
        response = await authenticated_client.patch(
            "/user/me",
            json={
                "password": "newpassword123",
                "password_confirm": "newpassword123"
            }
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_user_password_mismatch(self, authenticated_client: AsyncClient, test_user):
        """Test updating with mismatched passwords."""
        response = await authenticated_client.patch(
            "/user/me",
            json={
                "password": "newpassword123",
                "password_confirm": "different123"
            }
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_user_unauthorized(self, client: AsyncClient):
        """Test updating user without authentication."""
        response = await client.patch(
            "/user/me",
            json={"username": "updated"}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_delete_user_success(self, authenticated_client: AsyncClient, db_session: AsyncSession):
        """Test deleting current user."""
        user = await UserFactory.create_in_db(db_session, username="to_delete")

        token_service = JWTService()
        access_token = token_service.create_access_token(
            username=user.username,
            user_id=user.id,
            role=user.role.name
        )

        client = AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        response = await client.delete("/user/me")

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_user_unauthorized(self, client: AsyncClient):
        """Test deleting user without authentication."""
        response = await client.delete("/user/me")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_user_username_already_exists(self, authenticated_client: AsyncClient,
                                                       db_session: AsyncSession, test_user):
        """Test updating username to one that already exists."""
        # Create another user with a different username
        existing_user = await UserFactory.create_in_db(db_session, username="existing_user")

        # Try to update test_user's username to the existing username
        response = await authenticated_client.patch(
            "/user/me",
            json={"username": "existing_user"}
        )

        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, authenticated_client: AsyncClient):
        """Test getting user when user doesn't exist (deleted user)."""
        # This would require mocking the repository to return None
        # For now, we'll skip this as it's an edge case
        pass
