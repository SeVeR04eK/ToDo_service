from fastapi import APIRouter, Depends, status, Path
from typing import Annotated

from app.models import User
from app.schemas import UserRead, TaskRead, TaskUpdate
from app.authorization import require_role
from app.api.deps import db
from app.services import AdminService, TaskService

admin_router = APIRouter(prefix = "/admin", tags = ["admin"])

@admin_router.get("/users", status_code=status.HTTP_200_OK, response_model=list[UserRead])
async def get_users(
        _: Annotated[
            User,
            Depends(require_role("admin"))
        ],
        session: db
):

    service = AdminService(session)

    return await service.get_users_service()

@admin_router.get("/users/{user_id}", status_code=status.HTTP_200_OK, response_model=UserRead)
async def get_user(
        _: Annotated[
                    User,
                    Depends(require_role("admin"))
                ],
        user_id: Annotated[int, Path(..., title="User ID")],
        session: db
):

    service = AdminService(session=session)

    return await service.get_user_service(user_id)

@admin_router.patch("/users/{user_id}", status_code=status.HTTP_200_OK, response_model=UserRead)
async def ban_user(
        _: Annotated[
                    User,
                    Depends(require_role("admin"))
                ],
        user_id: Annotated[int, Path(..., title="User ID")],
        is_active: bool,
        session: db
):

    service = AdminService(session=session)

    return await service.ban_user_service(user_id, is_active)

@admin_router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        _: Annotated[
                    User,
                    Depends(require_role("admin"))
                ],
        user_id: Annotated[int, Path(..., title="User ID")],
        session: db
):

    service = AdminService(session=session)
    await service.delete_user_service(user_id)

    return True

@admin_router.get("/users/{user_id}/tasks", status_code=status.HTTP_200_OK, response_model=list[TaskRead])
async def get_tasks(
        _: Annotated[
                    User,
                    Depends(require_role("admin"))
                ],
        user_id: Annotated[int, Path(..., title="User ID")],
        session: db
):

    service = TaskService(session=session)

    return await service.get_tasks_service(user_id)

@admin_router.get("/users/{user_id}/tasks/{task_id}", status_code=status.HTTP_200_OK, response_model=TaskRead)
async def get_task(
        _: Annotated[
                    User,
                    Depends(require_role("admin"))
                ],
        user_id: Annotated[int, Path(..., title="User ID")],
        task_id: Annotated[int, Path(..., title="Task ID")],
        session: db
):

    service = TaskService(session=session)

    return await service.get_task_service(task_id, user_id)

@admin_router.patch("/users/{user_id}/tasks/{task_id}", status_code=status.HTTP_200_OK, response_model=TaskRead)
async def update_task(
        _: Annotated[
                    User,
                    Depends(require_role("admin"))
                ],
        task_id: Annotated[int, Path(..., title="Task ID")],
        user_id: Annotated[int, Path(..., title="User ID")],
        task_update: TaskUpdate,
        session: db
):

    service = TaskService(session=session)

    return await service.update_task_service(task_id, task_update, user_id)

@admin_router.delete("/users/{user_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
        _: Annotated[
                    User,
                    Depends(require_role("admin"))
                ],
        task_id: Annotated[int, Path(..., title="Task ID")],
        user_id: Annotated[int, Path(..., title="User ID")],
        session: db
):

    service = TaskService(session=session)
    await service.delete_task_service(task_id, user_id)

    return True