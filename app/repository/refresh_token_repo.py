from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select
from datetime import datetime, timezone

from app.models import RefreshToken


class RefreshTokenRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_refresh_token(self, user_id: int, token: str, expires: datetime) -> None:

        self.session.add(RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires)
        )
        await self.session.commit()

    async def delete_refresh_token_by_user_id(self, user_id: int) -> None:

        request = delete(RefreshToken).where(RefreshToken.user_id == user_id)
        await self.session.execute(request)
        await self.session.commit()

    async def delete_refresh_token(self, token: RefreshToken) -> None:

        await self.session.delete(token)
        await self.session.commit()

    async def get_token_expires(self, refresh_token: str) -> RefreshToken:

        request = select(RefreshToken).where(RefreshToken.token == refresh_token)

        return await self.session.scalar(request)

    async def delete_expired_tokens(self) -> None:

        now = datetime.now(timezone.utc)

        request = delete(RefreshToken).where(RefreshToken.expires_at < now)
        await self.session.execute(request)
        await self.session.commit()