from fastapi import APIRouter, status

from app.schemas import UserRead, UserCreate
from app.api.deps import db
from app.services.user_service import create_user

router = APIRouter(prefix="/user", tags=["user"])

@router.post("/create/", status_code=status.HTTP_201_CREATED, response_model=UserRead)
async def create_user_route(
        user: UserCreate,
        session: db
):
    return await create_user(user, session)



