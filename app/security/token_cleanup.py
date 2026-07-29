import asyncio
import logging

from app.domain.interfaces import RefreshTokenRepository
from app.repositories import SQLAlchemyRefreshTokenRepository
from app.db.database import SessionLocal

logger = logging.getLogger(__name__)


async def clean_tokens_task():
    """Background task to clean expired refresh tokens."""
    while True:
        try:
            async with SessionLocal() as session:
                repository: RefreshTokenRepository = SQLAlchemyRefreshTokenRepository(session)
                await repository.delete_expired_tokens()
                logger.info("Expired tokens cleaned successfully")
        except Exception as e:
            logger.error(f"Error cleaning expired tokens: {e}")

        await asyncio.sleep(7200)  # Run every 2 hours
