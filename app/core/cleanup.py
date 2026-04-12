from sqlalchemy import delete
from datetime import datetime, timezone
import asyncio

from app.models import RefreshToken
from app.db import get_session


async def clean_tokens_task():
    while True:
        async with get_session() as session:
            await session.execute(
                delete(RefreshToken)
                .where(RefreshToken.expires_at < datetime.now(timezone.utc))
            )
            await session.commit()

        await asyncio.sleep(7200)