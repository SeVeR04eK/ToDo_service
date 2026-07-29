from fastapi import APIRouter, status, Depends, HTTPException, Body
from typing import Annotated

from app.domain.entities import User
from app.schemas import UserRead, UserCreate, UserUpdate, UserRole
from app.api.dependencies import require_role
from app.services import UserService
from app.core.exceptions import UsernameAlreadyExistsError, UserNotFoundError
from app.api.dependencies.services_dep import get_user_service

# User router for user profile management
user_router = APIRouter(prefix = "/user", tags = ["user"])

@user_router.post("/me", status_code = status.HTTP_201_CREATED, response_model = UserRead, summary="User registration")
async def create_user(
        user: UserCreate,
        service: UserService = Depends(get_user_service)
) -> UserRead:
    """Register a new user (_public endpoint, no authentication required_)."""

    try:
        user = await service.create_user_service(user)
        return UserRead(
            id=user.id,
            username=user.username,
            is_active=user.is_active,
            role=UserRole(name=user.role.name) if user.role else None
        )
    except UsernameAlreadyExistsError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

@user_router.get("/me",status_code=status.HTTP_200_OK, response_model = UserRead, summary="Get user profile")
async def get_user(
        user: Annotated[
            User,
            Depends(require_role("user", "admin"))
        ],
        service: UserService = Depends(get_user_service)
) -> UserRead:
    """Get the **authenticated** user's profile."""

    try:
        user = await service.get_user_service(user.id)
        return UserRead(
            id=user.id,
            username=user.username,
            is_active=user.is_active,
            role=UserRole(name=user.role.name) if user.role else None
        )
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

@user_router.patch("/me",status_code=status.HTTP_200_OK, response_model = UserRead, summary="Update user profile")
async def update_user(
        user: Annotated[
            User,
            Depends(require_role("user", "admin"))
        ],
        user_update: Annotated[
            UserUpdate,
            Body(
                openapi_examples={
                    "full": {
                        "summary": "Update user profile with all fields.",
                        "description": "Update user profile with all fields: username, password, password_confirm",
                        "value": {
                            "username": "user",
                            "password": "user12345",
                            "password_confirm": "user12345"
                        }
                    },
                    "partial_username": {
                        "summary": "Update user profile with only the provided username.",
                        "description": "Update user profile with only the provided field: username",
                        "value": {
                            "username": "user"
                        }
                    },
                    "partial_password": {
                        "summary": "Update user profile with only the provided password.",
                        "description": "Update user profile with only the provided fields: password and password_confirm",
                        "value": {
                            "password": "user12345",
                            "password_confirm": "user12345"
                        }
                    },
                    "no_changes": {
                        "summary": "No fields provided",
                        "description": "PATCH request with no fields. Nothing will be updated.",
                        "value": {}
                    }
                }
            )
        ],
    service: UserService = Depends(get_user_service)
) -> UserRead:
    """Update the **authenticated** user's profile (_partial update_)."""

    try:
        user = await service.update_user_service(user_id=user.id, user_update=user_update)
        return UserRead(
            id=user.id,
            username=user.username,
            is_active=user.is_active,
            role=UserRole(name=user.role.name) if user.role else None
        )
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except UsernameAlreadyExistsError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

@user_router.delete("/me", status_code=status.HTTP_204_NO_CONTENT, summary="Delete user account")
async def delete_user(
        user: Annotated[
                    User,
                    Depends(require_role("user", "admin"))
                ],
        service: UserService = Depends(get_user_service)
) -> None:
    """Delete the **authenticated** user's account."""

    try:
        await service.delete_user_service(user.id)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")



