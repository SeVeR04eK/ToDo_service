from fastapi import APIRouter, status, Depends
from typing import Annotated

from app.models import User
from app.schemas import UserRead, UserCreate, UserUpdate
from app.api.dependencies import db, require_role
from app.services import UserService

# User router for user profile management
user_router = APIRouter(prefix = "/user", tags = ["user"])

@user_router.post("/me", status_code = status.HTTP_201_CREATED, response_model = UserRead)
async def create_user(
        user: UserCreate,
        session: db
):
    """Register a new user (public endpoint, no authentication required)."""

    service = UserService(session=session)
    return await service.create_user_service(user)

@user_router.get("/me",status_code=status.HTTP_200_OK, response_model = UserRead)
async def get_user(
        user: Annotated[
            User,
            Depends(require_role("user", "admin"))
        ]
):
    """Get the authenticated user's profile."""

    return await UserService.get_user_service(user)

@user_router.patch("/me",status_code=status.HTTP_200_OK, response_model = UserRead)
async def update_user(
        user: Annotated[
            User,
            Depends(require_role("user", "admin"))
        ],
        user_update: UserUpdate,
        session: db
):
    """Update the authenticated user's profile (partial update)."""

    service = UserService(session=session)

    return await service.update_user_service(user=user, user_update=user_update)

@user_router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        user: Annotated[
                    User,
                    Depends(require_role("user", "admin"))
                ],
        session: db
):
    """Delete the authenticated user's account."""

    service = UserService(session=session)

    await service.delete_user_service(user)

    # Return True to indicate successful deletion (FastAPI handles 204 response)
    return True



