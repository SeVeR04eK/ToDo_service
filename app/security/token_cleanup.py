import asyncio
import logging

from app.repositories import RefreshTokenRepository
from app.db import get_session

logger = logging.getLogger(__name__)


async def clean_tokens_task():
    """Background task to clean expired refresh tokens."""
    while True:
        try:
            async with get_session() as session:
                repository = RefreshTokenRepository(session)
                await repository.delete_expired_tokens()
                logger.info("Expired tokens cleaned successfully")
        except Exception as e:
            logger.error(f"Error cleaning expired tokens: {e}")
        
        await asyncio.sleep(7200)  # Run every 2 hours
