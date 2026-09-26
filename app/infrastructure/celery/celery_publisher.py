import structlog
from app.application.interfaces import MessagePublisher
from app.infrastructure.celery.email_task import send_welcome_email_task

logger = structlog.get_logger(__name__)


class CeleryMessagePublisher(MessagePublisher):
    """Celery-based message publisher for sending tasks to Celery workers."""

    async def publish_welcome_email(self, username: str, email: str) -> None:
        """Publish welcome email task to Celery.
        
        This sends a task to Celery workers instead of RabbitMQ queues.
        The task will be executed by a Celery worker with retry logic.
        
        Args:
            username: The username of the new user.
            email: The email address of the new user.
        """
        try:
            # Send task to Celery (non-blocking)
            send_welcome_email_task.delay(username, email)
            
            logger.info(
                "Welcome email task published to Celery",
                username=username,
                email=email
            )
        except Exception as e:
            logger.error(
                "Failed to publish welcome email task to Celery",
                username=username,
                email=email,
                error=str(e)
            )
            # Re-raise to allow caller to handle the error
            raise


_publisher: CeleryMessagePublisher | None = None


def get_celery_publisher() -> CeleryMessagePublisher:
    """Get or create the Celery message publisher (lazy initialization).
    
    Returns:
        CeleryMessagePublisher: Celery message publisher instance.
    """
    global _publisher
    if _publisher is None:
        _publisher = CeleryMessagePublisher()
    return _publisher
