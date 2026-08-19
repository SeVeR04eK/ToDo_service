"""Tests for AuthService."""
import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone, timedelta
from jose import jwt

from app.application.services import AuthService
from app.domain.interfaces import UnitOfWork, TokenService, TokenHasher
from app.domain.entities import User, Role, RefreshToken
from app.domain.exceptions import InvalidRefreshTokenError, UserNotFoundError
from app.core import settings


@pytest.mark.unit
class TestAuthService:
    """Test AuthService business logic."""

    @pytest.mark.asyncio
    async def test_authentication_service_success(self):
        """Test successful authentication."""
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.refresh_token_repository = AsyncMock()
        mock_token_service = AsyncMock(spec=TokenService)
        mock_auth_use_case = AsyncMock()
        
        mock_role = Role(id=1, name="user")
        mock_user = User(id=1, username="testuser", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_auth_use_case.execute.return_value = mock_user
        mock_uow.refresh_token_repository.create_refresh_token.return_value = None
        mock_token_service.create_access_token.return_value = "access_token"
        mock_token_service.create_refresh_token.return_value = ("refresh_token", datetime.now(timezone.utc) + timedelta(days=7))
        mock_uow.__aenter__.return_value = mock_uow
        mock_uow.commit.return_value = None
        
        mock_token_hasher = AsyncMock(spec=TokenHasher)
        mock_token_hasher.hash.return_value = "hashed_token"
        
        service = AuthService(
            unit_of_work=mock_uow,
            token_service=mock_token_service,
            authenticate_user_use_case=mock_auth_use_case,
            token_hasher=mock_token_hasher
        )
        
        tokens = await service.authentication_service(
            username="testuser",
            password="TestPassword123!"
        )
        
        assert tokens.access_token == "access_token"
        assert tokens.refresh_token == "refresh_token"
        assert tokens.token_type == "bearer"
        mock_uow.commit.assert_awaited_once()
        # Verify that revoke_token_by_user_id is NOT called (multiple sessions supported)
        mock_uow.refresh_token_repository.revoke_token_by_user_id.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_refresh_service_success(self):
        """Test successful token refresh."""
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.refresh_token_repository = AsyncMock()
        mock_uow.user_repository = AsyncMock()
        mock_token_service = AsyncMock(spec=TokenService)
        mock_auth_use_case = AsyncMock()

        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        created_at = datetime.now(timezone.utc)
        mock_token = RefreshToken(
            id=1,
            token_hash="hashed_valid_token",
            family_id="family-123",
            user_id=1,
            expires_at=expires_at,
            created_at=created_at,
            revoked_at=None
        )
        new_mock_token = RefreshToken(
            id=2,
            token_hash="hashed_new_token",
            family_id="family-123",
            user_id=1,
            expires_at=expires_at,
            created_at=created_at,
            revoked_at=None
        )
        mock_uow.refresh_token_repository.get_by_token_hash.return_value = mock_token
        mock_uow.user_repository.get_user_role.return_value = "user"
        mock_uow.refresh_token_repository.revoke_refresh_token.return_value = True
        mock_uow.refresh_token_repository.create_refresh_token.return_value = new_mock_token
        mock_token_service.decode_refresh_token.return_value = {"id": 1, "sub": "testuser"}
        mock_token_service.create_access_token.return_value = "new_access"
        mock_token_service.create_refresh_token.return_value = ("new_refresh", datetime.now(timezone.utc) + timedelta(days=7))
        mock_uow.__aenter__.return_value = mock_uow
        mock_uow.commit.return_value = None

        mock_token_hasher = AsyncMock(spec=TokenHasher)
        mock_token_hasher.hash.return_value = "hashed_token"

        service = AuthService(
            unit_of_work=mock_uow,
            token_service=mock_token_service,
            authenticate_user_use_case=mock_auth_use_case,
            token_hasher=mock_token_hasher
        )

        tokens = await service.refresh_service("valid_token")

        assert tokens.access_token == "new_access"
        assert tokens.refresh_token == "new_refresh"
        assert tokens.token_type == "bearer"
        mock_uow.commit.assert_awaited_once()
        # Verify revoke_refresh_token is called once with replaced_by parameter
        mock_uow.refresh_token_repository.revoke_refresh_token.assert_awaited_once_with(
            1, replaced_by=2
        )
        # Verify family_id is preserved during rotation
        mock_uow.refresh_token_repository.create_refresh_token.assert_awaited_once()
        call_kwargs = mock_uow.refresh_token_repository.create_refresh_token.call_args.kwargs
        assert call_kwargs["family_id"] == "family-123"

    @pytest.mark.asyncio
    async def test_refresh_service_invalid_token(self):
        """Test refresh with invalid token raises InvalidRefreshTokenError."""
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.refresh_token_repository = AsyncMock()
        mock_token_service = AsyncMock(spec=TokenService)
        mock_auth_use_case = AsyncMock()
        mock_uow.refresh_token_repository.get_by_token_hash.return_value = None
        
        mock_token_hasher = AsyncMock(spec=TokenHasher)
        mock_token_hasher.hash.return_value = "hashed_token"
        
        service = AuthService(
            unit_of_work=mock_uow,
            token_service=mock_token_service,
            authenticate_user_use_case=mock_auth_use_case,
            token_hasher=mock_token_hasher
        )
        
        with pytest.raises(InvalidRefreshTokenError):
            await service.refresh_service("invalid_token")

    @pytest.mark.asyncio
    async def test_refresh_service_expired_token(self):
        """Test refresh with expired token raises InvalidRefreshTokenError."""
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.refresh_token_repository = AsyncMock()
        mock_token_service = AsyncMock(spec=TokenService)
        mock_auth_use_case = AsyncMock()
        
        expired_time = datetime.now(timezone.utc) - timedelta(hours=1)
        created_at = datetime.now(timezone.utc) - timedelta(days=1)
        mock_token = RefreshToken(
            id=1,
            token_hash="hashed_expired_token",
            family_id="family-123",
            user_id=1,
            expires_at=expired_time,
            created_at=created_at,
            revoked_at=None
        )
        mock_uow.refresh_token_repository.get_by_token_hash.return_value = mock_token
        
        mock_token_hasher = AsyncMock(spec=TokenHasher)
        mock_token_hasher.hash.return_value = "hashed_token"
        
        service = AuthService(
            unit_of_work=mock_uow,
            token_service=mock_token_service,
            authenticate_user_use_case=mock_auth_use_case,
            token_hasher=mock_token_hasher
        )
        
        with pytest.raises(InvalidRefreshTokenError):
            await service.refresh_service("expired_token")

    @pytest.mark.asyncio
    async def test_refresh_service_user_not_found(self):
        """Test refresh when user doesn't exist raises InvalidRefreshTokenError (security measure)."""
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.refresh_token_repository = AsyncMock()
        mock_uow.user_repository = AsyncMock()
        mock_token_service = AsyncMock(spec=TokenService)
        mock_auth_use_case = AsyncMock()
        
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        created_at = datetime.now(timezone.utc)
        mock_token = RefreshToken(
            id=1,
            token_hash="hashed_valid_token",
            family_id="family-123",
            user_id=1,
            expires_at=expires_at,
            created_at=created_at,
            revoked_at=None
        )
        mock_uow.refresh_token_repository.get_by_token_hash.return_value = mock_token
        mock_uow.user_repository.get_user_role.return_value = None
        mock_token_service.decode_refresh_token.return_value = {"id": 1, "sub": "testuser"}
        
        mock_token_hasher = AsyncMock(spec=TokenHasher)
        mock_token_hasher.hash.return_value = "hashed_token"
        
        service = AuthService(
            unit_of_work=mock_uow,
            token_service=mock_token_service,
            authenticate_user_use_case=mock_auth_use_case,
            token_hasher=mock_token_hasher
        )
        
        with pytest.raises(InvalidRefreshTokenError):
            await service.refresh_service("valid_token")

    @pytest.mark.asyncio
    async def test_refresh_service_invalid_payload(self):
        """Test refresh with malformed token payload raises InvalidRefreshTokenError."""
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.refresh_token_repository = AsyncMock()
        mock_token_service = AsyncMock(spec=TokenService)
        mock_auth_use_case = AsyncMock()
        
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        created_at = datetime.now(timezone.utc)
        mock_token = RefreshToken(
            id=1,
            token_hash="hashed_invalid_payload_token",
            family_id="family-123",
            user_id=1,
            expires_at=expires_at,
            created_at=created_at,
            revoked_at=None
        )
        mock_uow.refresh_token_repository.get_by_token_hash.return_value = mock_token
        mock_token_service.decode_refresh_token.return_value = {"sub": "test"}  # Missing "id"
        
        mock_token_hasher = AsyncMock(spec=TokenHasher)
        mock_token_hasher.hash.return_value = "hashed_token"
        
        service = AuthService(
            unit_of_work=mock_uow,
            token_service=mock_token_service,
            authenticate_user_use_case=mock_auth_use_case,
            token_hasher=mock_token_hasher
        )
        
        with pytest.raises(InvalidRefreshTokenError):
            await service.refresh_service("invalid_payload_token")

    @pytest.mark.asyncio
    async def test_refresh_service_already_consumed(self):
        """Test refresh when token was already consumed by another request raises InvalidRefreshTokenError."""
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.refresh_token_repository = AsyncMock()
        mock_uow.user_repository = AsyncMock()
        mock_token_service = AsyncMock(spec=TokenService)
        mock_auth_use_case = AsyncMock()

        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        created_at = datetime.now(timezone.utc)
        mock_token = RefreshToken(
            id=1,
            token_hash="hashed_consumed_token",
            family_id="family-123",
            user_id=1,
            expires_at=expires_at,
            created_at=created_at,
            revoked_at=None
        )
        new_mock_token = RefreshToken(
            id=2,
            token_hash="hashed_new_token",
            family_id="family-123",
            user_id=1,
            expires_at=expires_at,
            created_at=created_at,
            revoked_at=None
        )
        mock_uow.refresh_token_repository.get_by_token_hash.return_value = mock_token
        mock_uow.user_repository.get_user_role.return_value = "user"
        mock_uow.refresh_token_repository.create_refresh_token.return_value = new_mock_token
        mock_uow.refresh_token_repository.revoke_refresh_token.return_value = False  # Already revoked
        mock_token_service.decode_refresh_token.return_value = {"id": 1, "sub": "testuser"}
        mock_token_service.create_access_token.return_value = "new_access"
        mock_token_service.create_refresh_token.return_value = ("new_refresh", datetime.now(timezone.utc) + timedelta(days=7))
        mock_uow.__aenter__.return_value = mock_uow

        mock_token_hasher = AsyncMock(spec=TokenHasher)
        mock_token_hasher.hash.return_value = "hashed_token"

        service = AuthService(
            unit_of_work=mock_uow,
            token_service=mock_token_service,
            authenticate_user_use_case=mock_auth_use_case,
            token_hasher=mock_token_hasher
        )

        with pytest.raises(InvalidRefreshTokenError):
            await service.refresh_service("consumed_token")

        mock_uow.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_refresh_tokens_have_unique_jti(self):
        """Test that two refresh tokens generated immediately after each other have different jti claims."""
        from app.infrastructure.services.jwt_service import JWTService

        token_service = JWTService()

        # Generate two refresh tokens in quick succession
        token1, expires1 = await token_service.create_refresh_token(
            username="testuser",
            user_id=1
        )

        token2, expires2 = await token_service.create_refresh_token(
            username="testuser",
            user_id=1
        )

        # Decode both tokens
        payload1 = jwt.decode(
            token1,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorithm],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
        )

        payload2 = jwt.decode(
            token2,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorithm],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
        )

        # Verify both have jti claims
        assert "jti" in payload1
        assert "jti" in payload2

        # Verify the jti claims are different
        assert payload1["jti"] != payload2["jti"]

        # Verify other claims are the same (same user, same second)
        assert payload1["sub"] == payload2["sub"]
        assert payload1["id"] == payload2["id"]
        assert payload1["iat"] == payload2["iat"]
