from fastapi import APIRouter, status, Depends, Path, Query, HTTPException
from typing import Annotated, Optional

from app.models import User
from app.schemas import TaskCreate, TaskRead, TaskUpdate, TaskStatus, TasksPagination
from app.api.dependencies import db, require_role, tasks_pagination
from app.services import TaskService
from app.core.exceptions import TaskNotFoundError


# Tasks router for task management (accessible by users and admins)
tasks_router = APIRouter(prefix = "/tasks", tags = ["tasks"])

@tasks_router.post("/me", status_code = status.HTTP_201_CREATED, response_model = TaskRead, summary="Create a new task")
async def create_task(
        user: Annotated[
            User,
            Depends(require_role("user", "admin"))
        ],
        task: TaskCreate,
        session: db
) -> TaskRead:
    """Create a new task for the **authenticated** user."""

    service = TaskService(session=session)

    return TaskRead.model_validate(await service.create_task_service(task, user.id))

@tasks_router.get("/me", status_code=status.HTTP_200_OK, response_model=list[TaskRead], summary="Get all user's tasks")
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
        pagination: TasksPagination = Depends(tasks_pagination)
    ) -> list[TaskRead]:
    """Get all tasks for the **authenticated** user with optional _filtering_ and _pagination_:
    - **task_status**: Optional task status filter
    - **limit**: Number of tasks to return
    - **offset**: Number of tasks to skip
    - **from_newest**: Boolean to sort tasks from the newest first
    """

    service = TaskService(session=session)

    return [TaskRead.model_validate(task) for task in await service.get_tasks_service(
        user_id=user.id,
        task_status=task_status,
        pagination=pagination
    )]

@tasks_router.get("/me/{task_id}", status_code=status.HTTP_200_OK, response_model=TaskRead, summary="Get specific task")
async def get_task(
        user: Annotated[
                    User,
                    Depends(require_role("user", "admin"))
                ],
        task_id: Annotated[int, Path(..., title="Task ID")],
        session: db
) -> TaskRead:
    """Get a specific task by ID for the **authenticated** user."""

    try:
        service = TaskService(session=session)
        return TaskRead.model_validate(await service.get_task_service(task_id=task_id, user_id=user.id))
    except TaskNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

@tasks_router.patch("/me/{task_id}", status_code=status.HTTP_200_OK, response_model=TaskRead, summary="Update task")
async def update_task(
        user: Annotated[
                    User,
                    Depends(require_role("user", "admin"))
                ],
        task_id: Annotated[int, Path(..., title="Task ID")],
        task_update: TaskUpdate,
        session: db
) -> TaskRead:
    """Update a specific task by ID for the **authenticated** user (_partial update_)."""

    try:
        service = TaskService(session=session)
        return TaskRead.model_validate(await service.update_task_service(task_id=task_id, user_id=user.id, task_update=task_update))
    except TaskNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

@tasks_router.delete("/me/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete task")
async def delete_task(
        user: Annotated[
                    User,
                    Depends(require_role("user", "admin"))
                ],
        task_id: Annotated[int, Path(..., title="Task ID")],
        session: db
) -> None:
    """Delete a specific task by ID for the **authenticated** user."""

    try:
        service = TaskService(session=session)
        await service.delete_task_service(task_id=task_id, user_id=user.id)
    except TaskNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")