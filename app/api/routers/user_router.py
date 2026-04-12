from fastapi import APIRouter, status, Depends
from typing import Annotated

from app.models import User
from app.schemas import UserRead, UserCreate
from app.api.deps import db
from app.authorization import require_role
from app.services import UserService


user_router = APIRouter(prefix = "/user", tags = ["user"])

@user_router.post("/create_user", status_code = status.HTTP_201_CREATED, response_model = UserRead)
async def create_user(
        user: UserCreate,
        session: db
):

    service = UserService(session)
    return await service.create_user_service(user)

@user_router.get("/get_user", response_model = UserRead)
async def get_user(
        user: Annotated[
            User,
            Depends(require_role("user", "admin"))
        ]
):

    return await UserService.get_user_service(user)



