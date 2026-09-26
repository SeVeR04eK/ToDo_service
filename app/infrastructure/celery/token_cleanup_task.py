import asyncio
import structlog
from celery import Task
from app.infrastructure.celery.celery_app import celery_app
from app.infrastructure.database import SessionLocal
from app.infrastructure.repositories import SQLAlchemyRefreshTokenRepository

logger = structlog.get_logger(__name__)


class TokenCleanupTask(Task):
    """Base task for token cleanup operations with database session management."""

    pass


@celery_app.task(
    bind=True,
    base=TokenCleanupTask,
    name="app.infrastructure.celery.token_cleanup_task.clean_expired_tokens_task"
)
def clean_expired_tokens_task(self) -> int:
    """Clean expired refresh tokens from the database.
    
    This is a periodic task executed by Celery Beat to remove expired
    refresh tokens from the database.
    """
    try:
        logger.info(
            "Starting token cleanup via Celery",
            task_id=self.request.id
        )
        
        async def cleanup_tokens():
            async with SessionLocal() as session:
                repository = SQLAlchemyRefreshTokenRepository(session)
                await repository.delete_expired_tokens()
                await session.commit()
                logger.info("Expired tokens cleaned successfully via Celery")
                return 0  # We don't track count, just success

        result = asyncio.run(
            cleanup_tokens()
        )
        
        logger.info(
            "Token cleanup completed successfully via Celery",
            task_id=self.request.id
        )
        
        return result
        
    except Exception as exc:
        logger.exception(
            "Error during token cleanup via Celery",
            task_id=self.request.id,
            error=str(exc)
        )
        # Don't retry - this is a periodic task that will run again
        raise
