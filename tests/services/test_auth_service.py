"""Tests for AuthService."""
import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth_service import AuthService
from app.core.exceptions import InvalidTokenError, UserNotFoundError


@pytest.mark.unit
class TestAuthService:
    """Test AuthService business logic."""

    @pytest.mark.asyncio
    async def test_authentication_service_success(self, db_session: AsyncSession, test_user):
        """Test successful authentication."""
        service = AuthService(session=db_session)
        
        tokens = await service.authentication_service(
            username=test_user.username,
            password="TestPassword123!"
        )
        
        assert tokens.access_token is not None
        assert tokens.refresh_token is not None
        assert tokens.token_type == "bearer"

    @pytest.mark.asyncio
    async def test_refresh_service_success(self, db_session: AsyncSession, test_user):
        """Test successful token refresh."""
        from app.security import create_refresh_token
        
        # Create a refresh token
        refresh_token = await create_refresh_token(
            username=test_user.username,
            user_id=test_user.id,
            session=db_session
        )
        
        service = AuthService(session=db_session)
        tokens = await service.refresh_service(refresh_token)
        
        assert tokens.access_token is not None
        assert tokens.refresh_token is not None
        assert tokens.token_type == "bearer"

    @pytest.mark.asyncio
    async def test_refresh_service_invalid_token(self, db_session: AsyncSession):
        """Test refresh with invalid token raises InvalidTokenError."""
        service = AuthService(session=db_session)
        
        with pytest.raises(InvalidTokenError):
            await service.refresh_service("invalid_token")

    @pytest.mark.asyncio
    async def test_refresh_service_expired_token(self, db_session: AsyncSession, test_user):
        """Test refresh with expired token raises InvalidTokenError."""
        from app.models import RefreshToken
        from jose import jwt
        from app.core import settings
        
        # Create an expired token directly in DB
        expired_time = datetime.now(timezone.utc) - timedelta(hours=1)
        payload = {"sub": test_user.username, "id": test_user.id, "exp": int(expired_time.timestamp())}
        expired_token_str = jwt.encode(payload, settings.secret_key.get_secret_value(), algorithm=settings.algorithm)
        
        expired_token = RefreshToken(
            token=expired_token_str,
            user_id=test_user.id,
            expires_at=expired_time
        )
        
        db_session.add(expired_token)
        await db_session.commit()
        
        service = AuthService(session=db_session)
        
        with pytest.raises(InvalidTokenError):
            await service.refresh_service(expired_token_str)

    @pytest.mark.asyncio
    async def test_refresh_service_user_not_found(self, db_session: AsyncSession, test_user):
        """Test refresh when user doesn't exist raises UserNotFoundError."""
        from app.security import create_refresh_token
        
        # Create a refresh token
        refresh_token = await create_refresh_token(
            username=test_user.username,
            user_id=test_user.id,
            session=db_session
        )
        
        # Delete the user
        await db_session.delete(test_user)
        await db_session.commit()
        
        service = AuthService(session=db_session)
        
        with pytest.raises(UserNotFoundError):
            await service.refresh_service(refresh_token)

    @pytest.mark.asyncio
    async def test_refresh_service_invalid_payload(self, db_session: AsyncSession):
        """Test refresh with malformed token payload raises HTTPException."""
        from app.models import RefreshToken
        from jose import jwt
        from app.core import settings
        from fastapi import HTTPException
        
        # Create a token with invalid payload (missing id or sub)
        invalid_payload = {"sub": "test"}  # Missing "id"
        valid_time = datetime.now(timezone.utc) + timedelta(hours=1)
        invalid_payload["exp"] = int(valid_time.timestamp())
        invalid_token = jwt.encode(invalid_payload, settings.secret_key.get_secret_value(), algorithm=settings.algorithm)
        
        # Add to DB as valid token
        token = RefreshToken(
            token=invalid_token,
            user_id=1,
            expires_at=valid_time
        )
        
        db_session.add(token)
        await db_session.commit()
        
        service = AuthService(session=db_session)
        
        with pytest.raises(HTTPException):
            await service.refresh_service(invalid_token)
