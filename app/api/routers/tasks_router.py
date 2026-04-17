from fastapi import APIRouter, status, Depends, Path, Query
from typing import Annotated, Optional

from app.models import User
from app.schemas import TaskCreate, TaskRead, TaskUpdate, TaskStatus
from app.api.deps import db
from app.authorization import require_role
from app.services import TaskService


tasks_router = APIRouter(prefix = "/tasks", tags = ["tasks"])

@tasks_router.post("/me", status_code = status.HTTP_201_CREATED, response_model = TaskRead)
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

@tasks_router.get("/me", status_code=status.HTTP_200_OK, response_model=list[TaskRead])
async def get_tasks(
        user: Annotated[
                    User,
                    Depends(require_role("user", "admin"))
                ],
        session: db,
        task_status: Annotated[
            Optional[TaskStatus],
            Query(title="Task Status")
        ] = None,
        limit: Annotated[
            Optional[int],
            Query(title="Limit of tasks", ge=1, le=100)
        ] = None,
        from_newest: Annotated[
            Optional[bool],
            Query(title="Sort from newest")] = False,
):

    service = TaskService(session=session)

    return await service.get_tasks_service(
        user_id=user.id,
        task_status=task_status,
        limit=limit,
        from_newest=from_newest
    )

@tasks_router.get("/me/{task_id}", status_code=status.HTTP_200_OK, response_model=TaskRead)
async def get_task(
        user: Annotated[
                    User,
                    Depends(require_role("user", "admin"))
                ],
        task_id: Annotated[int, Path(..., title="Task ID")],
        session: db
):

    service = TaskService(session=session)

    return await service.get_task_service(task_id, user.id)

@tasks_router.patch("/me/{task_id}", status_code=status.HTTP_200_OK, response_model=TaskRead)
async def update_task(
        user: Annotated[
                    User,
                    Depends(require_role("user", "admin"))
                ],
        task_id: Annotated[int, Path(..., title="Task ID")],
        task_update: TaskUpdate,
        session: db
):

    service = TaskService(session=session)

    return await service.update_task_service(task_id, task_update, user.id)

@tasks_router.delete("/me/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
        user: Annotated[
                    User,
                    Depends(require_role("user", "admin"))
                ],
        task_id: Annotated[int, Path(..., title="Task ID")],
        session: db
):

    service = TaskService(session=session)
    await service.delete_task_service(task_id, user.id)

    return True