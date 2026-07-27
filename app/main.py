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
    version="0.0.1",
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
