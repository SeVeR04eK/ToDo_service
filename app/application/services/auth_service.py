from datetime import datetime, timezone
import structlog

from app.domain.exceptions import UserNotFoundError, InvalidRefreshTokenError
from app.application.dto import Tokens
from app.domain.interfaces import UnitOfWork, TokenService
from app.application.use_cases import AuthenticateUserUseCase

logger = structlog.get_logger(__name__)


class AuthService:
    """Service layer for authentication and token management."""

    def __init__(
            self,
            unit_of_work: UnitOfWork,
            token_service: TokenService,
            authenticate_user_use_case: AuthenticateUserUseCase
    ):
        self.unit_of_work = unit_of_work
        self.token_service = token_service
        self.authenticate_user_use_case = authenticate_user_use_case

    async def authentication_service(self, username: str, password: str) -> Tokens:
        """Authenticate user and return access/refresh tokens."""

        logger.info(
            "User login attempt",
            username=username,
        )
        
        user = await self.authenticate_user_use_case.execute(username, password)

        async with self.unit_of_work:
            # Invalidate all existing refresh tokens for this user (single session per user)
            await self.unit_of_work.refresh_token_repository.delete_refresh_token_by_user_id(user.id)

            access_token = self.token_service.create_access_token(
                username = user.username,
                user_id = user.id,
                role = user.role.name if user.role else None
            )
            refresh_token, expires = await self.token_service.create_refresh_token(
                username = user.username,
                user_id = user.id,
            )

            await self.unit_of_work.refresh_token_repository.create_refresh_token(
                user_id=user.id,
                token=refresh_token,
                expires=expires
            )

            await self.unit_of_work.commit()

        logger.info(
            "User logged in successfully",
            user_id=user.id,
            username=user.username,
        )

        return Tokens(
            refresh_token=refresh_token,
            access_token=access_token,
            token_type="bearer"
        )

    async def refresh_service(self, refresh_token: str) -> Tokens:
        """Refresh access token using a valid refresh token."""

        logger.info("Token refresh attempt")

        # Decode the refresh token to get user information first
        payload = self.token_service.decode_refresh_token(refresh_token)

        if "id" not in payload or "sub" not in payload:
            logger.warning("Invalid refresh token payload")
            raise InvalidRefreshTokenError()

        user_id = payload["id"]
        username = payload["sub"]

        # Check if user exists
        user_role = await self.unit_of_work.user_repository.get_user_role(user_id)

        if user_role is None:
            logger.warning("User not found during token refresh", user_id=user_id)
            raise UserNotFoundError()

        # Check token expiration
        db_token = await self.unit_of_work.refresh_token_repository.get_token_expires(refresh_token)

        if db_token is None:
            logger.warning("Refresh token not found")
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
            logger.warning("Refresh token expired")
            raise InvalidRefreshTokenError()

        async with self.unit_of_work:
            # Atomically consume the used refresh token (token rotation)
            # This prevents race conditions where multiple concurrent requests
            # could both read the same token and try to consume it
            consumed = await self.unit_of_work.refresh_token_repository.consume_refresh_token(refresh_token)

            if not consumed:
                # Token was already consumed by another request
                logger.warning("Refresh token already consumed", user_id=user_id)
                raise InvalidRefreshTokenError()

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

            await self.unit_of_work.refresh_token_repository.create_refresh_token(
                user_id=user_id,
                token=new_refresh,
                expires=expires
            )

            await self.unit_of_work.commit()

        logger.info(
            "Token refreshed successfully",
            user_id=user_id,
            username=username,
        )

        return Tokens(
            refresh_token=new_refresh,
            access_token=new_access,
            token_type="bearer"
        )