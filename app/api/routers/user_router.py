from fastapi import APIRouter, status, Depends
from typing import Annotated

from app.schemas import UserRead, UserCreate
from app.api.deps import db, get_current_user
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
            dict,
            Depends(get_current_user)
        ],
        session: db
):

    service = UserService(session)
    return await service.get_user_service(user["id"])



