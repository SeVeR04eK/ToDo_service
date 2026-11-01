import structlog
from fastapi import APIRouter, status, HTTPException
from datetime import datetime, timezone
from sqlalchemy import text
from app.infrastructure.database import SessionLocal
from app.infrastructure.redis import get_redis_client
import aio_pika
from app.core.config import settings

logger = structlog.get_logger(__name__)
health_router = APIRouter(prefix="/health", tags=["health"])


@health_router.get("/ready", summary="Readiness check")
async def health_check():
    """Checks whether the application is ready to serve requests by verifying its service dependencies."""

    db_status = "healthy"

    try:
        async with SessionLocal() as session:
            await session.execute(text("SELECT 1"))
    except Exception:
        logger.exception("PostgreSQL health check failed")
        db_status = "unhealthy"

    redis_status = "healthy"

    try:
        redis = get_redis_client()
        await redis.ping()
    except Exception:
        logger.exception("Redis health check failed")
        redis_status = "unhealthy"

    rabbitmq_status = "healthy"

    try:
        connection = await aio_pika.connect_robust(settings.celery_broker_url)
        await connection.close()
    except Exception:
        logger.exception("RabbitMQ health check failed")
        rabbitmq_status = "unhealthy"

    overall_healthy = (
        db_status == "healthy"
        and redis_status == "healthy"
        and rabbitmq_status == "healthy"
    )

    response = {
        "status": "healthy" if overall_healthy else "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "ToDo Service API",
        "version": "1.0.0",
        "dependencies": {
            "database": db_status,
            "redis": redis_status,
            "rabbitmq": rabbitmq_status,
        },
    }

    if not overall_healthy:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=response
        )

    return response

@health_router.get("/live", status_code=status.HTTP_200_OK, summary="Liveness check")
async def live():
    """Liveness check to verify that the application is running."""
    return {"status": "alive"}