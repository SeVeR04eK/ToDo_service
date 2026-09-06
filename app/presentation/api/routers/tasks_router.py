from fastapi import APIRouter, status, Depends, Path, Query, Body
from typing import Annotated, Optional, List

from app.domain.entities import User
from app.presentation.api.schemas import TaskCreate, TaskRead, TaskUpdate, TasksPagination, PaginatedResponse, PaginationMeta, DataResponse
from app.domain.enums import TaskStatus
from app.application.dto import TaskPaginationDTO, CreateTaskDTO, UpdateTaskDTO
from app.presentation.api.dependencies import require_role, tasks_pagination, rate_limit_auth
from app.application.services import TaskService
from app.presentation.api.dependencies.services_dep import get_task_service
from app.core.config import settings


# Tasks router for task management (accessible by users and admins)
tasks_router = APIRouter(prefix = "/tasks", tags = ["tasks"])

@tasks_router.post("/me", status_code = status.HTTP_201_CREATED, response_model = DataResponse[TaskRead], summary="Create a new task")
async def create_task(
        user: Annotated[
            User,
            Depends(require_role("user", "admin"))
        ],
        task: TaskCreate,
        service: TaskService = Depends(get_task_service),
        _rate_limit: Annotated[None, Depends(rate_limit_auth(
            key_prefix="tasks_create",
            limit=settings.rate_limit_tasks_create_limit,
            window=settings.rate_limit_tasks_create_window,
            algorithm="sliding_window_counter"
        ))] = None,
) -> DataResponse[TaskRead]:
    """Create a new task for the **authenticated** user."""

    task_dto = CreateTaskDTO(
        title=task.title,
        content=task.content,
        status=task.status
    )

    task = await service.create_task_service(task_dto, user.id)

    return DataResponse[TaskRead](
        data=TaskRead(
            id=task.id,
            title=task.title,
            content=task.content,
            status=task.status,
            user_id=task.user_id
        )
    )

@tasks_router.get("/me", status_code=status.HTTP_200_OK, response_model=PaginatedResponse[TaskRead], summary="Get all user's tasks")
async def get_tasks(
        user: Annotated[
                    User,
                    Depends(require_role("user", "admin"))
                ],
        service: TaskService = Depends(get_task_service),
        task_status: Annotated[
            Optional[TaskStatus],
            Query(title="Task Status")
        ] = None,
        pagination: TasksPagination = Depends(tasks_pagination),
        _rate_limit: Annotated[None, Depends(rate_limit_auth(
            key_prefix="tasks_read",
            limit=settings.rate_limit_tasks_read_limit,
            window=settings.rate_limit_tasks_read_window,
            algorithm="sliding_window_counter"
        ))] = None,
    ) -> PaginatedResponse[TaskRead]:
    """Get all tasks for the **authenticated** user with optional _filtering_ and _pagination_:
    - **task_status**: Optional task status filter
    - **limit**: Number of tasks to return
    - **offset**: Number of tasks to skip
    - **from_newest**: Boolean to sort tasks from the newest first
    """

    pagination_dto = TaskPaginationDTO(
        limit=pagination.limit,
        offset=pagination.offset,
        from_newest=pagination.from_newest
    )

    page = await service.get_tasks_service(
        user_id=user.id,
        task_status=task_status,
        pagination=pagination_dto
    )

    return PaginatedResponse[TaskRead](
        data=[
            TaskRead(
                id=task.id,
                title=task.title,
                content=task.content,
                status=task.status,
                user_id=task.user_id
            )
            for task in page.items
        ],
        meta=PaginationMeta(
            page=page.page,
            page_size=page.page_size,
            total_items=page.total_items,
            total_pages=page.total_pages,
            has_next=page.has_next,
            has_previous=page.has_previous
        )
    )

@tasks_router.get("/me/{task_id}", status_code=status.HTTP_200_OK, response_model=DataResponse[TaskRead], summary="Get specific task")
async def get_task(
        user: Annotated[
                    User,
                    Depends(require_role("user", "admin"))
                ],
        task_id: Annotated[int, Path(..., title="Task ID")],
        service: TaskService = Depends(get_task_service),
        _rate_limit: Annotated[None, Depends(rate_limit_auth(
            key_prefix="tasks_read",
            limit=settings.rate_limit_tasks_read_limit,
            window=settings.rate_limit_tasks_read_window,
            algorithm="sliding_window_counter"
        ))] = None,
) -> DataResponse[TaskRead]:
    """Get a specific task by ID for the **authenticated** user."""


    task = await service.get_task_service(task_id=task_id, user_id=user.id)
    return DataResponse[TaskRead](
        data=TaskRead(
            id=task.id,
            title=task.title,
            content=task.content,
            status=task.status,
            user_id=task.user_id
        )
    )

@tasks_router.patch("/me/{task_id}", status_code=status.HTTP_200_OK, response_model=DataResponse[TaskRead], summary="Update task")
async def update_task(
        user: Annotated[
                    User,
                    Depends(require_role("user", "admin"))
                ],
        task_id: Annotated[int, Path(..., title="Task ID")],
        task_update: Annotated[
            TaskUpdate,
            Body(
                openapi_examples={
                    "full": {
                        "summary": "Update user task with all fields.",
                        "description": "Update user task with all fields: title, content, status",
                        "value": {
                            "title": "example new title",
                            "content": "example new content",
                            "status": "done"
                        }
                    },
                    "partial_title": {
                        "summary": "Update user task with only the provided title.",
                        "description": "Update user task with only the provided field: title",
                        "value": {
                            "title": "example new title"
                        }
                    },
                    "partial_content": {
                        "summary": "Update user task with only the provided content.",
                        "description": "Update user task with only the provided field: content",
                        "value": {
                            "content": "example new content"
                        }
                    },
                    "partial_status": {
                        "summary": "Update user task with only the provided status.",
                        "description": "Update user task with only the provided field: status",
                        "value": {
                            "status": "done"
                        }
                    },
                    "partial_two_fields": {
                        "summary": "Update user task with only provided two fields.",
                        "description": "Update user task with only the provided field: title, status",
                        "value": {
                            "title": "example new title",
                            "status": "done"
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
        service: TaskService = Depends(get_task_service),
        _rate_limit: Annotated[None, Depends(rate_limit_auth(
            key_prefix="tasks_update",
            limit=settings.rate_limit_tasks_update_limit,
            window=settings.rate_limit_tasks_update_window,
            algorithm="sliding_window_counter"
        ))] = None,
) -> DataResponse[TaskRead]:
    """Update a specific task by ID for the **authenticated** user (_partial update_)."""


    task_dto = UpdateTaskDTO(
        title=task_update.title,
        content=task_update.content,
        status=task_update.status
    )

    task = await service.update_task_service(task_id=task_id, user_id=user.id, task_update=task_dto)
    return DataResponse[TaskRead](
        data=TaskRead(
            id=task.id,
            title=task.title,
            content=task.content,
            status=task.status,
            user_id=task.user_id
        )
    )

@tasks_router.delete("/me/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete task")
async def delete_task(
        user: Annotated[
                    User,
                    Depends(require_role("user", "admin"))
                ],
        task_id: Annotated[int, Path(..., title="Task ID")],
        service: TaskService = Depends(get_task_service),
        _rate_limit: Annotated[None, Depends(rate_limit_auth(
            key_prefix="tasks_delete",
            limit=settings.rate_limit_tasks_delete_limit,
            window=settings.rate_limit_tasks_delete_window,
            algorithm="sliding_window_counter"
        ))] = None,
) -> None:
    """Delete a specific task by ID for the **authenticated** user."""

    await service.delete_task_service(task_id=task_id, user_id=user.id)