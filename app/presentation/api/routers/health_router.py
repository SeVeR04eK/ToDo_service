from fastapi import APIRouter, status
from datetime import datetime, timezone
from sqlalchemy import text
from app.infrastructure.database import SessionLocal
from app.infrastructure.redis import get_redis_client

health_router = APIRouter(prefix="/health", tags=["health"])


@health_router.get("/", status_code=status.HTTP_200_OK, summary="Health check")
async def health_check():
    """Health check endpoint to verify service dependencies."""

    db_status = "healthy"
    db_error = None

    try:
        async with SessionLocal() as session:
            await session.execute(text("SELECT 1"))
    except Exception as e:
        db_status = "unhealthy"
        db_error = str(e)

    redis_status = "healthy"
    redis_error = None

    try:
        redis = get_redis_client()
        await redis.ping()
    except Exception as e:
        redis_status = "unhealthy"
        redis_error = str(e)

    overall_status = (
        "healthy"
        if db_status == "healthy" and redis_status == "healthy"
        else "degraded"
    )

    return {
        "status": overall_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "ToDo Service API",
        "version": "0.4.0",
        "database": {
            "status": db_status,
            "error": db_error,
        },
        "redis": {
            "status": redis_status,
            "error": redis_error,
        },
    }
