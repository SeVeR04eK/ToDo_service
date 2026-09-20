import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio

from app.core.logging import setup_logging, settings
from app.presentation.api import api_router
from app.infrastructure.background_tasks import clean_tokens_task
from app.domain.exceptions.base import DomainException
from app.presentation.exception_handlers import domain_exception_handler
from app.presentation.api.middleware import setup_middlewares
from app.infrastructure.messaging.rabbitmq_consumer import RabbitMQConsumer
from app.infrastructure.messaging.rabbitmq_publisher import get_rabbitmq_publisher
from app.infrastructure.services.email_service import EmailService

# Initialize logging before creating the FastAPI app
# Skip logging setup during tests to avoid pollution
if os.getenv("PYTEST_RUNNING") != "true":
    setup_logging()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application lifespan manager.
    
    This context manager handles startup and shutdown events:
    - Startup: Start the background task to clean expired refresh tokens and RabbitMQ consumer
    - Shutdown: Cancel the background task gracefully and close RabbitMQ connection
    """
    # Start background task for cleaning expired tokens
    token_task = asyncio.create_task(clean_tokens_task())
    
    # Start RabbitMQ consumer
    email_service = EmailService()
    rabbitmq_consumer = RabbitMQConsumer(email_service)
    consumer_task = None
    
    try:
        await rabbitmq_consumer.connect()
        consumer_task = asyncio.create_task(rabbitmq_consumer.start_consuming())
    except Exception as e:
        import structlog
        logger = structlog.get_logger(__name__)
        logger.error("Failed to start RabbitMQ consumer", error=str(e))

    # Properly handle the lifespan
    try:
        yield
    finally:
        # Cancel background task on shutdown
        token_task.cancel()
        
        if consumer_task:
            consumer_task.cancel()
        
        await rabbitmq_consumer.close()
        
        # Close RabbitMQ publisher
        rabbitmq_publisher = get_rabbitmq_publisher()
        await rabbitmq_publisher.close()

        try:
            await token_task
        except asyncio.CancelledError:
            pass
        
        if consumer_task:
            try:
                await consumer_task
            except asyncio.CancelledError:
                pass


tags_metadata = [
    {
        "name": "auth",
        "description": "Endpoints for user authentication and JWT token refresh.",
    },
    {
        "name": "user",
        "description": "Endpoints for managing the **authenticated** user's profile.",
    },
    {
        "name": "tasks",
        "description": "CRUD operations for tasks belonging to the authenticated user.",
    },
    {
        "name": "admin",
        "description": "Admin-only endpoints for managing users, roles, and user tasks.",
    }
]

# Create FastAPI application with custom lifespan and metadata
app = FastAPI(
    lifespan=lifespan,
    title="ToDo Service",
    description="""
### About the Project
The **ToDo Service** is a clean and modern backend application designed to help users manage their daily tasks.  
It focuses on simplicity, clarity, and a smooth developer experience.

### What It Does
- Allows users to create, update, and delete tasks  
- Provides secure user registration and authentication  
- Organizes all functionality through a structured REST API

### Why It Exists
This project serves as a practical example of building a well‑organized backend using FastAPI.  
It demonstrates how to design a reliable, secure, and easy‑to‑maintain API suitable for real applications and learning.
    """,
    summary="Task management API with authentication.",
    version="0.5.1",
    contact={
        "name": "Andrii Severyn",
        "email": "andrej.chees.bs@gmail.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://mit-license.org",
    },
    openapi_tags=tags_metadata
)
# Include all API routers
app.include_router(api_router)
app.add_exception_handler(
    DomainException,
    domain_exception_handler,
)

# Add middleware (order matters - correlation ID must be first)
setup_middlewares(app, settings)