from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio

from app.api import api_router
from app.security import clean_tokens_task

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application lifespan manager.
    
    This context manager handles startup and shutdown events:
    - Startup: Start the background task to clean expired refresh tokens
    - Shutdown: Cancel the background task gracefully
    """
    # Start background task for cleaning expired tokens
    task = asyncio.create_task(clean_tokens_task())

    yield

    # Cancel background task on shutdown
    task.cancel()


# Create FastAPI application with custom lifespan
app = FastAPI(lifespan=lifespan)
# Include all API routers
app.include_router(api_router)