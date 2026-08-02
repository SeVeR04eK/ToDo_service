"""Tests for AuthService."""
import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone, timedelta

from app.application.services import AuthService
from app.domain.interfaces import UserRepository, RefreshTokenRepository, TokenService
from app.domain.entities import User, Role, RefreshToken
from app.domain.exceptions import InvalidRefreshTokenError, UserNotFoundError


@pytest.mark.unit
class TestAuthService:
    """Test AuthService business logic."""

    @pytest.mark.asyncio
    async def test_authentication_service_success(self):
        """Test successful authentication."""
        mock_user_repo = AsyncMock(spec=UserRepository)
        mock_refresh_repo = AsyncMock(spec=RefreshTokenRepository)
        mock_token_service = AsyncMock(spec=TokenService)
        mock_auth_use_case = AsyncMock()
        
        mock_role = Role(id=1, name="user")
        mock_user = User(id=1, username="testuser", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_auth_use_case.execute.return_value = mock_user
        mock_refresh_repo.delete_refresh_token_by_user_id.return_value = None
        mock_refresh_repo.create_refresh_token.return_value = None
        mock_token_service.create_access_token.return_value = "access_token"
        mock_token_service.create_refresh_token.return_value = ("refresh_token", datetime.now(timezone.utc) + timedelta(days=7))
        
        service = AuthService(
            user_repository=mock_user_repo,
            refresh_token_repository=mock_refresh_repo,
            token_service=mock_token_service,
            authenticate_user_use_case=mock_auth_use_case
        )
        
        tokens = await service.authentication_service(
            username="testuser",
            password="TestPassword123!"
        )
        
        assert tokens.access_token == "access_token"
        assert tokens.refresh_token == "refresh_token"
        assert tokens.token_type == "bearer"

    @pytest.mark.asyncio
    async def test_refresh_service_success(self):
        """Test successful token refresh."""
        mock_user_repo = AsyncMock(spec=UserRepository)
        mock_refresh_repo = AsyncMock(spec=RefreshTokenRepository)
        mock_token_service = AsyncMock(spec=TokenService)
        mock_auth_use_case = AsyncMock()
        
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        mock_token = RefreshToken(id=1, token="valid_token", user_id=1, expires_at=expires_at)
        mock_refresh_repo.get_token_expires.return_value = mock_token
        mock_user_repo.get_user_role.return_value = "user"
        mock_refresh_repo.delete_refresh_token.return_value = None
        mock_refresh_repo.create_refresh_token.return_value = None
        mock_token_service.decode_refresh_token.return_value = {"id": 1, "sub": "testuser"}
        mock_token_service.create_access_token.return_value = "new_access"
        mock_token_service.create_refresh_token.return_value = ("new_refresh", datetime.now(timezone.utc) + timedelta(days=7))
        
        service = AuthService(
            user_repository=mock_user_repo,
            refresh_token_repository=mock_refresh_repo,
            token_service=mock_token_service,
            authenticate_user_use_case=mock_auth_use_case
        )
        
        tokens = await service.refresh_service("valid_token")
        
        assert tokens.access_token == "new_access"
        assert tokens.refresh_token == "new_refresh"
        assert tokens.token_type == "bearer"

    @pytest.mark.asyncio
    async def test_refresh_service_invalid_token(self):
        """Test refresh with invalid token raises InvalidRefreshTokenError."""
        mock_user_repo = AsyncMock(spec=UserRepository)
        mock_refresh_repo = AsyncMock(spec=RefreshTokenRepository)
        mock_token_service = AsyncMock(spec=TokenService)
        mock_auth_use_case = AsyncMock()
        mock_refresh_repo.get_token_expires.return_value = None
        
        service = AuthService(
            user_repository=mock_user_repo,
            refresh_token_repository=mock_refresh_repo,
            token_service=mock_token_service,
            authenticate_user_use_case=mock_auth_use_case
        )
        
        with pytest.raises(InvalidRefreshTokenError):
            await service.refresh_service("invalid_token")

    @pytest.mark.asyncio
    async def test_refresh_service_expired_token(self):
        """Test refresh with expired token raises InvalidRefreshTokenError."""
        mock_user_repo = AsyncMock(spec=UserRepository)
        mock_refresh_repo = AsyncMock(spec=RefreshTokenRepository)
        mock_token_service = AsyncMock(spec=TokenService)
        mock_auth_use_case = AsyncMock()
        
        expired_time = datetime.now(timezone.utc) - timedelta(hours=1)
        mock_token = RefreshToken(id=1, token="expired_token", user_id=1, expires_at=expired_time)
        mock_refresh_repo.get_token_expires.return_value = mock_token
        
        service = AuthService(
            user_repository=mock_user_repo,
            refresh_token_repository=mock_refresh_repo,
            token_service=mock_token_service,
            authenticate_user_use_case=mock_auth_use_case
        )
        
        with pytest.raises(InvalidRefreshTokenError):
            await service.refresh_service("expired_token")

    @pytest.mark.asyncio
    async def test_refresh_service_user_not_found(self):
        """Test refresh when user doesn't exist raises UserNotFoundError."""
        mock_user_repo = AsyncMock(spec=UserRepository)
        mock_refresh_repo = AsyncMock(spec=RefreshTokenRepository)
        mock_token_service = AsyncMock(spec=TokenService)
        mock_auth_use_case = AsyncMock()
        
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        mock_token = RefreshToken(id=1, token="valid_token", user_id=1, expires_at=expires_at)
        mock_refresh_repo.get_token_expires.return_value = mock_token
        mock_user_repo.get_user_role.return_value = None
        mock_token_service.decode_refresh_token.return_value = {"id": 1, "sub": "testuser"}
        
        service = AuthService(
            user_repository=mock_user_repo,
            refresh_token_repository=mock_refresh_repo,
            token_service=mock_token_service,
            authenticate_user_use_case=mock_auth_use_case
        )
        
        with pytest.raises(UserNotFoundError):
            await service.refresh_service("valid_token")

    @pytest.mark.asyncio
    async def test_refresh_service_invalid_payload(self):
        """Test refresh with malformed token payload raises InvalidRefreshTokenError."""
        mock_user_repo = AsyncMock(spec=UserRepository)
        mock_refresh_repo = AsyncMock(spec=RefreshTokenRepository)
        mock_token_service = AsyncMock(spec=TokenService)
        mock_auth_use_case = AsyncMock()
        
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        mock_token = RefreshToken(id=1, token="invalid_payload_token", user_id=1, expires_at=expires_at)
        mock_refresh_repo.get_token_expires.return_value = mock_token
        mock_token_service.decode_refresh_token.return_value = {"sub": "test"}  # Missing "id"
        
        service = AuthService(
            user_repository=mock_user_repo,
            refresh_token_repository=mock_refresh_repo,
            token_service=mock_token_service,
            authenticate_user_use_case=mock_auth_use_case
        )
        
        with pytest.raises(InvalidRefreshTokenError):
            await service.refresh_service("invalid_payload_token")
