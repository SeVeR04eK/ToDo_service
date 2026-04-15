from fastapi import APIRouter, status, Depends
from typing import Annotated

from app.models import User
from app.schemas import TaskCreate, TaskRead
from app.api.deps import db
from app.authorization import require_role
from app.services import TaskService


tasks_router = APIRouter(prefix = "/tasks", tags = ["tasks"])

@tasks_router.post("/create_task", status_code = status.HTTP_201_CREATED, response_model = TaskRead)
async def create_task(
        user: Annotated[
            User,
            Depends(require_role("user", "admin"))
        ],
        task: TaskCreate,
        session: db
):

    service = TaskService(session=session)
    return await service.create_task_service(task, user.id)