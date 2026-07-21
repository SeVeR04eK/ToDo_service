from fastapi import status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.repositories import RefreshTokenRepository, UserRepository
from app.security import authenticate_user, create_access_token, create_refresh_token, decode_refresh_token
from app.schemas import TokensResponse


class AuthService:
    """Service layer for authentication and token management."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def authentication_service(self, form_data: OAuth2PasswordRequestForm) -> TokensResponse:
        """Authenticate user and return access/refresh tokens."""

        user = await authenticate_user(form_data.username, form_data.password, self.session)

        repository = RefreshTokenRepository(session=self.session)
        # Invalidate all existing refresh tokens for this user (single session per user)
        await repository.delete_refresh_token_by_user_id(user.id)

        access_token = create_access_token(
            username = user.username,
            user_id = user.id,
            role = user.role.name
        )
        refresh_token = await create_refresh_token(
            username = user.username,
            user_id = user.id,
            session = self.session
        )

        return TokensResponse(refresh_token = refresh_token, access_token = access_token, token_type = "bearer")

    async def refresh_service(self, refresh_token: str) -> TokensResponse:
        """Refresh access token using a valid refresh token."""

        refresh_repository = RefreshTokenRepository(session=self.session)
        db_token = await refresh_repository.get_token_expires(refresh_token)

        # Handle timezone comparison - SQLite returns naive datetimes
        if db_token is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")
        
        # Make both datetimes comparable by ensuring they're both naive or both aware
        expires_at = db_token.expires_at
        if expires_at.tzinfo is None:
            # If db_token is naive, compare with naive UTC time
            now = datetime.now(timezone.utc).replace(tzinfo=None)
        else:
            # If db_token is aware, compare with aware UTC time
            now = datetime.now(timezone.utc)
        
        if expires_at < now:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")

        # Decode the refresh token to get user information
        payload = decode_refresh_token(refresh_token)
        username = payload["sub"]
        user_id = payload["id"]

        # Delete the used refresh token (token rotation)
        await refresh_repository.delete_refresh_token(db_token)

        user_repository = UserRepository(session=self.session)
        user_role = await user_repository.get_user_role(user_id)

        if user_role is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")

        # Issue new tokens
        new_refresh = await create_refresh_token(
            username=username,
            user_id=user_id,
            session=self.session
        )
        new_access = create_access_token(
            username=username,
            user_id=user_id,
            role=user_role
        )

        return TokensResponse(refresh_token = new_refresh, access_token = new_access, token_type = "bearer")