from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select
from datetime import datetime, timezone

from app.models import RefreshToken


class RefreshTokenRepository:
    """Repository for refresh token database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_refresh_token(self, user_id: int, token: str, expires: datetime) -> None:
        """Create a new refresh token for a user."""

        self.session.add(RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires)
        )
        await self.session.commit()

    async def delete_refresh_token_by_user_id(self, user_id: int) -> None:
        """Delete all refresh tokens for a user (used on logout)."""

        request = delete(RefreshToken).where(RefreshToken.user_id == user_id)
        await self.session.execute(request)
        await self.session.commit()

    async def delete_refresh_token(self, token: RefreshToken) -> None:
        """Delete a specific refresh token."""

        await self.session.delete(token)
        await self.session.commit()

    async def get_token_expires(self, refresh_token: str) -> RefreshToken | None:
        """Get a refresh token by its value to check expiration."""

        request = select(RefreshToken).where(RefreshToken.token == refresh_token)

        return await self.session.scalar(request)

    async def delete_expired_tokens(self) -> None:
        """Delete all expired refresh tokens (cleanup operation)."""

        now = datetime.now(timezone.utc)

        request = delete(RefreshToken).where(RefreshToken.expires_at < now)
        await self.session.execute(request)
        await self.session.commit()