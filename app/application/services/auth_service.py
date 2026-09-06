from datetime import datetime, timezone
import structlog
import uuid

from app.domain.exceptions import InvalidRefreshTokenError, InvalidCredentialsError
from app.application.dto import Tokens
from app.domain.interfaces import UnitOfWork, TokenService
from app.domain.entities import RefreshToken
from app.application.use_cases import AuthenticateUserUseCase
from app.domain.interfaces import TokenHasher
from app.core import settings

logger = structlog.get_logger(__name__)


class AuthService:
    """Service layer for authentication and token management."""

    def __init__(
            self,
            unit_of_work: UnitOfWork,
            token_service: TokenService,
            authenticate_user_use_case: AuthenticateUserUseCase,
            token_hasher: TokenHasher
    ):
        self.unit_of_work = unit_of_work
        self.token_service = token_service
        self.authenticate_user_use_case = authenticate_user_use_case
        self.token_hasher = token_hasher


    async def revoke_token_and_raise(self, db_token: RefreshToken):
        await self.unit_of_work.refresh_token_repository.revoke_family_by_id(db_token.family_id)
        await self.unit_of_work.commit()
        raise InvalidRefreshTokenError()


    async def authentication_service(self, username: str, password: str) -> Tokens:
        """Authenticate user and return access/refresh tokens."""

        logger.info(
            "login_attempt",
            username=username,
        )
        
        try:
            user = await self.authenticate_user_use_case.execute(username, password)
        except InvalidCredentialsError:
            logger.warning(
                "login_failed",
                username=username,
                reason="invalid_credentials"
            )
            raise

        async with self.unit_of_work:
            # Create new refresh token without revoking existing ones (support multiple sessions)
            access_token = self.token_service.create_access_token(
                username=user.username,
                user_id=user.id,
                role=user.role.name if user.role else None
            )
            refresh_token, expires = await self.token_service.create_refresh_token(
                username=user.username,
                user_id=user.id,
            )

            # Hash the refresh token for storage
            token_hash = self.token_hasher.hash(refresh_token)
            # Generate a family ID for this token
            family_id = str(uuid.uuid4())

            await self.unit_of_work.refresh_token_repository.create_refresh_token(
                user_id=user.id,
                token_hash=token_hash,
                family_id=family_id,
                expires=expires
            )

            await self.unit_of_work.commit()

        logger.info(
            "login_success",
            user_id=user.id,
            username=user.username,
        )

        expires_in = int(settings.access_token_expire_minutes.total_seconds())

        return Tokens(
            refresh_token=refresh_token,
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_in
        )

    async def refresh_service(self, refresh_token: str) -> Tokens:
        """Refresh access token using a valid refresh token with rotation and reuse detection."""

        logger.info("refresh_attempt")

        # Decode the refresh token to get user information first
        payload = self.token_service.decode_refresh_token(refresh_token)

        if "id" not in payload or "sub" not in payload:
            logger.warning("refresh_failed", reason="invalid_payload")
            raise InvalidRefreshTokenError()

        user_id = payload["id"]
        username = payload["sub"]

        # Check if user exists
        user_role = await self.unit_of_work.user_repository.get_user_role(user_id)

        if user_role is None:
            logger.warning("refresh_failed", user_id=user_id, reason="user_not_found")
            raise InvalidRefreshTokenError()

        # Hash the token to look it up in the database
        token_hash = self.token_hasher.hash(refresh_token)

        # Get the token from database
        db_token = await self.unit_of_work.refresh_token_repository.get_by_token_hash(token_hash)

        if db_token is None:
            logger.warning("refresh_failed", user_id=user_id, reason="token_not_found")
            raise InvalidRefreshTokenError()

        # Check if token is already revoked (reuse detection)
        if db_token.revoked_at is not None:
            logger.warning(
                "refresh_token_reuse_detected",
                user_id=user_id,
                family_id=db_token.family_id,
                token_id=db_token.id
            )
            # Revoke the entire family as a security measure
            await self.revoke_token_and_raise(db_token)

        # Check token expiration
        now = datetime.now(timezone.utc)

        expires_at = db_token.expires_at
        if expires_at.tzinfo is None:
            now = now.replace(tzinfo=None)

        if db_token.expires_at < now:
            logger.warning("refresh_failed", user_id=user_id, reason="token_expired")
            raise InvalidRefreshTokenError()

        # Check family expiration
        family_created_at = db_token.family_created_at
        if family_created_at.tzinfo is None:
            now = now.replace(tzinfo=None)

        if db_token.family_created_at + settings.family_token_expire_days <= now:
            logger.warning("refresh_failed", user_id=user_id, reason="family_token_expired")
            await self.revoke_token_and_raise(db_token)

        async with self.unit_of_work:
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

            # Hash the new refresh token
            new_token_hash = self.token_hasher.hash(new_refresh)
            # Use the same family ID for token rotation
            family_id = db_token.family_id

            new_db_token = await self.unit_of_work.refresh_token_repository.create_refresh_token(
                user_id=user_id,
                token_hash=new_token_hash,
                family_id=family_id,
                expires=expires,
                family_created_at=db_token.family_created_at
            )

            # Revoke the old token and link it to the new one (token rotation)
            revoked = await self.unit_of_work.refresh_token_repository.revoke_refresh_token(
                db_token.id,
                replaced_by=new_db_token.id
            )

            if not revoked:
                # Token was already revoked by another request (race condition)
                logger.warning("refresh_failed", user_id=user_id, reason="token_already_revoked")
                raise InvalidRefreshTokenError()

            await self.unit_of_work.commit()

        logger.info(
            "refresh_success",
            user_id=user_id,
            username=username,
            family_id=family_id,
        )

        expires_in = int(settings.access_token_expire_minutes.total_seconds())

        return Tokens(
            refresh_token=new_refresh,
            access_token=new_access,
            token_type="bearer",
            expires_in=expires_in
        )

    async def logout_service(self, refresh_token: str) -> None:
        """Logout by revoking the current refresh token."""

        logger.info("logout_attempt")

        # Hash the token to look it up
        token_hash = self.token_hasher.hash(refresh_token)

        # Get the token from database
        db_token = await self.unit_of_work.refresh_token_repository.get_by_token_hash(token_hash)

        if db_token is None:
            logger.warning("logout_failed", reason="token_not_found")
            raise InvalidRefreshTokenError()

        async with self.unit_of_work:
            # Revoke the token
            await self.unit_of_work.refresh_token_repository.revoke_refresh_token(db_token.id)
            await self.unit_of_work.commit()

        logger.info(
            "logout_success",
            user_id=db_token.user_id,
            family_id=db_token.family_id,
        )

    async def logout_all_service(self, user_id: int) -> None:
        """Logout by revoking all refresh tokens for the user."""

        logger.info("logout_all_attempt", user_id=user_id)

        async with self.unit_of_work:
            # Revoke all tokens for the user
            await self.unit_of_work.refresh_token_repository.revoke_token_by_user_id(user_id)
            await self.unit_of_work.commit()

        logger.info("logout_all_success", user_id=user_id)