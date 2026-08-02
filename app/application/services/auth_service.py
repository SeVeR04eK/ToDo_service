from datetime import datetime, timezone

from app.domain.exceptions import UserNotFoundError, InvalidRefreshTokenError
from app.application.dto import Tokens
from app.domain.interfaces import UserRepository, RefreshTokenRepository, TokenService
from app.application.use_cases import AuthenticateUserUseCase


class AuthService:
    """Service layer for authentication and token management."""

    def __init__(
            self,
            user_repository: UserRepository,
            refresh_token_repository: RefreshTokenRepository,
            token_service: TokenService,
            authenticate_user_use_case: AuthenticateUserUseCase
    ):
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository
        self.token_service = token_service
        self.authenticate_user_use_case = authenticate_user_use_case

    async def authentication_service(self, username: str, password: str) -> Tokens:
        """Authenticate user and return access/refresh tokens."""

        user = await self.authenticate_user_use_case.execute(username, password)

        # Invalidate all existing refresh tokens for this user (single session per user)
        await self.refresh_token_repository.delete_refresh_token_by_user_id(user.id)

        access_token = self.token_service.create_access_token(
            username = user.username,
            user_id = user.id,
            role = user.role.name if user.role else None
        )
        refresh_token, expires = await self.token_service.create_refresh_token(
            username = user.username,
            user_id = user.id,
        )

        await self.refresh_token_repository.create_refresh_token(
            user_id=user.id,
            token=refresh_token,
            expires=expires
        )

        return Tokens(
            refresh_token=refresh_token,
            access_token=access_token,
            token_type="bearer"
        )

    async def refresh_service(self, refresh_token: str) -> Tokens:
        """Refresh access token using a valid refresh token."""

        db_token = await self.refresh_token_repository.get_token_expires(refresh_token)

        # Handle timezone comparison - SQLite returns naive datetimes
        if db_token is None:
            raise InvalidRefreshTokenError()

        # Make both datetimes comparable by ensuring they're both naive or both aware
        expires_at = db_token.expires_at
        if expires_at.tzinfo is None:
            # If db_token is naive, compare with naive UTC time
            now = datetime.now(timezone.utc).replace(tzinfo=None)
        else:
            # If db_token is aware, compare with aware UTC time
            now = datetime.now(timezone.utc)

        if expires_at < now:
            raise InvalidRefreshTokenError()

        # Decode the refresh token to get user information
        payload = self.token_service.decode_refresh_token(refresh_token)

        if "id" not in payload or "sub" not in payload:
            raise InvalidRefreshTokenError()

        user_id = payload["id"]

        user_role = await self.user_repository.get_user_role(user_id)

        if user_role is None:
            raise UserNotFoundError()

        # Delete the used refresh token (token rotation)
        await self.refresh_token_repository.delete_refresh_token(db_token)

        username = payload["sub"]

        # Issue new tokens
        new_refresh, expires = await self.token_service.create_refresh_token(
            username=username,
            user_id=user_id
        )

        new_access = self.token_service.create_access_token(
            username=username,
            user_id=user_id,
            role=user_role
        )

        await self.refresh_token_repository.create_refresh_token(
            user_id=user_id,
            token=new_refresh,
            expires=expires
        )

        return Tokens(
            refresh_token=new_refresh,
            access_token=new_access,
            token_type="bearer"
        )