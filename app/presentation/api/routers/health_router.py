from fastapi import APIRouter, status
from datetime import datetime, timezone
from sqlalchemy import text
from app.infrastructure.database import SessionLocal

health_router = APIRouter(prefix="/health", tags=["health"])


@health_router.get("/", status_code=status.HTTP_200_OK, summary="Health check")
async def health_check():
    """Health check endpoint to verify service and database connectivity."""

    # Check database connectivity
    db_status = "healthy"
    db_error = None

    try:
        async with SessionLocal() as session:
            await session.execute(text("SELECT 1"))
    except Exception as e:
        db_status = "unhealthy"
        db_error = str(e)

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "ToDo Service API",
        "version": "0.3.0",
        "database": {
            "status": db_status,
            "error": db_error
        }
    }
