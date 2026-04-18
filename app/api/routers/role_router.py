from fastapi import APIRouter

from app.schemas import RoleRead
from app.api.deps import db
from app.repository import get_roles

roles_router = APIRouter(prefix = "/roles", tags = ["roles"])

@roles_router.get("/", response_model=list[RoleRead])
async def get_roles_list(session: db):

    roles = await get_roles(session)

    return [RoleRead.model_validate(role) for role in roles]