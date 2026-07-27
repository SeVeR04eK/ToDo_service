from fastapi import APIRouter, status, Depends, HTTPException
from typing import Annotated

from app.models import User
from app.schemas import UserRead, UserCreate, UserUpdate
from app.api.dependencies import db, require_role
from app.services import UserService
from app.core.exceptions import UsernameAlreadyExistsError, UserNotFoundError

# User router for user profile management
user_router = APIRouter(prefix = "/user", tags = ["user"])

@user_router.post("/me", status_code = status.HTTP_201_CREATED, response_model = UserRead, summary="User registration")
async def create_user(
        user: UserCreate,
        session: db
) -> UserRead:
    """Register a new user (_public endpoint, no authentication required_)."""

    try:
        service = UserService(session=session)
        return UserRead.model_validate(await service.create_user_service(user))
    except UsernameAlreadyExistsError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

@user_router.get("/me",status_code=status.HTTP_200_OK, response_model = UserRead, summary="Get user profile")
async def get_user(
        user: Annotated[
            User,
            Depends(require_role("user", "admin"))
        ],
        session: db
) -> UserRead:
    """Get the **authenticated** user's profile."""

    try:
        service = UserService(session=session)
        return UserRead.model_validate(await service.get_user_service(user.id))
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

@user_router.patch("/me",status_code=status.HTTP_200_OK, response_model = UserRead, summary="Update user profile")
async def update_user(
        user: Annotated[
            User,
            Depends(require_role("user", "admin"))
        ],
        user_update: UserUpdate,
        session: db
) -> UserRead:
    """Update the **authenticated** user's profile (_partial update_)."""

    try:
        service = UserService(session=session)
        return UserRead.model_validate(await service.update_user_service(user_id=user.id, user_update=user_update))
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

@user_router.delete("/me", status_code=status.HTTP_204_NO_CONTENT, summary="Delete user account")
async def delete_user(
        user: Annotated[
                    User,
                    Depends(require_role("user", "admin"))
                ],
        session: db
) -> None:
    """Delete the **authenticated** user's account."""

    try:
        service = UserService(session=session)
        await service.delete_user_service(user.id)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")



