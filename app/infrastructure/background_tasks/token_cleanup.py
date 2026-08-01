import asyncio
import logging

from app.domain.interfaces import RefreshTokenRepository
from app.infrastructure.database import SessionLocal
from app.presentation.api.dependencies.repositories_dep import get_refresh_token_repository_raw

logger = logging.getLogger(__name__)


async def clean_tokens_task():
    """Background task to clean expired refresh tokens."""
    while True:
        try:
            async with SessionLocal() as session:
                repository: RefreshTokenRepository = get_refresh_token_repository_raw(session)
                await repository.delete_expired_tokens()
                logger.info("Expired tokens cleaned successfully")
        except Exception as e:
            logger.error(f"Error cleaning expired tokens: {e}")

        await asyncio.sleep(7200)  # Run every 2 hours
