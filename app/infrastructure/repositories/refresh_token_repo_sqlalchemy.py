from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select, update
from datetime import datetime, timezone
from typing import Optional

from app.infrastructure.models import RefreshToken as RefreshTokenORM
from app.domain.entities import RefreshToken
from app.infrastructure.mappers import refresh_token_from_orm
from app.domain.interfaces import RefreshTokenRepository


class SQLAlchemyRefreshTokenRepository(RefreshTokenRepository):
    """Repository for refresh token database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_refresh_token(
        self,
        user_id: int,
        token_hash: str,
        family_id: str,
        expires: datetime,
    ) -> RefreshToken:
        """Create a new refresh token for a user."""

        now = datetime.now(timezone.utc)
        orm_token = RefreshTokenORM(
            user_id=user_id,
            token_hash=token_hash,
            family_id=family_id,
            expires_at=expires,
            created_at=now,
        )
        self.session.add(orm_token)
        await self.session.flush()
        await self.session.refresh(orm_token)
        return refresh_token_from_orm(orm_token)

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

    async def revoke_refresh_token(
        self,
        token_id: int,
        replaced_by: Optional[int] = None,
    ) -> bool:
        """Revoke a refresh token by ID and optionally set the replacement token."""

        now = datetime.now(timezone.utc)
        stmt = (
            update(RefreshTokenORM)
            .where(RefreshTokenORM.id == token_id)
            .where(RefreshTokenORM.revoked_at.is_(None))
            .values(revoked_at=now, replaced_by=replaced_by)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0  # type: ignore[attr-defined]

    async def get_by_token_hash(self, token_hash: str) -> RefreshToken | None:
        """Get a refresh token by its hash."""

        request = select(RefreshTokenORM).where(RefreshTokenORM.token_hash == token_hash)
        orm_token = await self.session.scalar(request)
        return refresh_token_from_orm(orm_token) if orm_token else None

    async def revoke_family_by_id(self, family_id: str) -> None:
        """Revoke all tokens in a family by family ID."""

        now = datetime.now(timezone.utc)
        stmt = (
            update(RefreshTokenORM)
            .where(RefreshTokenORM.family_id == family_id)
            .where(RefreshTokenORM.revoked_at.is_(None))
            .values(revoked_at=now)
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def revoke_token_by_user_id(self, user_id: int) -> None:
        """Revoke all active refresh token families for a user."""

        now = datetime.now(timezone.utc)
        stmt = (
            update(RefreshTokenORM)
            .where(RefreshTokenORM.user_id == user_id)
            .where(RefreshTokenORM.revoked_at.is_(None))
            .values(revoked_at=now)
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def delete_expired_tokens(self) -> None:
        """Delete all expired refresh tokens (cleanup operation)."""

        now = datetime.now(timezone.utc)
        request = delete(RefreshTokenORM).where(RefreshTokenORM.expires_at < now)
        await self.session.execute(request)