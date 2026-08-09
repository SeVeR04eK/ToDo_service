from typing import cast
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select, CursorResult
from datetime import datetime, timezone

from app.infrastructure.models import RefreshToken as RefreshTokenORM
from app.domain.entities import RefreshToken
from app.infrastructure.mappers import refresh_token_from_orm
from app.domain.interfaces import RefreshTokenRepository


class SQLAlchemyRefreshTokenRepository(RefreshTokenRepository):
    """Repository for refresh token database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_refresh_token(self, user_id: int, token: str, expires: datetime) -> None:
        """Create a new refresh token for a user."""

        self.session.add(RefreshTokenORM(
            user_id=user_id,
            token=token,
            expires_at=expires)
        )

    async def delete_refresh_token_by_user_id(self, user_id: int) -> None:
        """Delete all refresh tokens for a user (used on logout)."""

        request = delete(RefreshTokenORM).where(RefreshTokenORM.user_id == user_id)
        await self.session.execute(request)
        await self.session.flush()

    async def delete_refresh_token(self, token: RefreshToken) -> None:
        """Delete a specific refresh token."""

        # Use atomic delete by ID to prevent race conditions
        request = delete(RefreshTokenORM).where(RefreshTokenORM.id == token.id)
        await self.session.execute(request)
        await self.session.flush()

    async def consume_refresh_token(self, refresh_token: str) -> bool:
        """Atomically delete a refresh token by its value and return True if deleted, False if not found."""

        request = delete(RefreshTokenORM).where(RefreshTokenORM.token == refresh_token)
        result = cast(CursorResult, await self.session.execute(request))
        await self.session.flush()
        return result.rowcount() > 0

    async def get_token_expires(self, refresh_token: str) -> RefreshToken | None:
        """Get a refresh token by its value to check expiration."""

        request = select(RefreshTokenORM).where(RefreshTokenORM.token == refresh_token)

        orm_token = await self.session.scalar(request)
        return refresh_token_from_orm(orm_token) if orm_token else None

    async def delete_expired_tokens(self) -> None:
        """Delete all expired refresh tokens (cleanup operation)."""

        now = datetime.now(timezone.utc)

        request = delete(RefreshTokenORM).where(RefreshTokenORM.expires_at < now)
        await self.session.execute(request)