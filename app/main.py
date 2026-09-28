import os
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.logging import setup_logging, settings
from app.presentation.api import api_router
from app.domain.exceptions.base import DomainException
from app.presentation.exception_handlers import domain_exception_handler
from app.presentation.api.middleware import setup_middlewares

# Initialize logging before creating the FastAPI app
# Skip logging setup during tests to avoid pollution
if os.getenv("PYTEST_RUNNING") != "true":
    setup_logging()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application lifespan manager.
    
    This context manager handles startup and shutdown events.
    Background tasks (email sending and token cleanup) are now handled by Celery workers.
    """
    # Properly handle the lifespan
    try:
        yield
    finally:
        # No background tasks to clean up - handled by Celery
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
    version="0.5.2",
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