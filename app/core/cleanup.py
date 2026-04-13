import asyncio

from app.repository import RefreshTokenRepository
from app.db import get_session


async def clean_tokens_task():
    while True:
        async with get_session() as session:

            repository = RefreshTokenRepository(session)
            await repository.delete_expired_tokens()

        await asyncio.sleep(7200)