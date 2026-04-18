from fastapi import APIRouter, Depends, status, Path, Query
from typing import Annotated, Optional

from app.models import User
from app.schemas import UserRead, TaskRead, TaskUpdate, TaskStatus, RoleRead, UserPermission, RoleCreate
from app.authorization import require_role
from app.api.deps import db
from app.services import AdminService, TaskService
from app.repository import AdminRepository

admin_router = APIRouter(prefix = "/admin", tags = ["admin"])

@admin_router.get("/users", status_code=status.HTTP_200_OK, response_model=list[UserRead]|UserRead)
async def get_users(
        _: Annotated[
            User,
            Depends(require_role("admin"))
        ],
        session: db,
        username: Annotated[
            Optional[str],
            Query(title="Username")
        ] = None,
        limit: Annotated[
            Optional[int],
            Query(title="Limit of users", ge=1, le=100)
        ] = None,
        offset: Annotated[
            Optional[int],
            Query(title="Limit of users", ge=1, le=100)
        ] = None
):

    service = AdminService(session)

    return await service.get_users_service(username=username, limit=limit, offset=offset)

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
async def user_permission(
        _: Annotated[
                    User,
                    Depends(require_role("admin"))
                ],
        user_id: Annotated[int, Path(..., title="User ID")],
        user_perm: UserPermission,
        session: db
):

    service = AdminService(session=session)

    return await service.permission_user_service(user_id=user_id, user_permission=user_perm)

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
        session: db,
        task_status: Annotated[
            Optional[TaskStatus],
            Query(title="Task Status")
        ] = None,
        limit: Annotated[
            Optional[int],
            Query(title="Limit of tasks", ge=1, le=100)
        ] = None,
        offset: Annotated[
            Optional[int],
            Query(title="Limit of tasks", ge=1, le=100)
        ] = None,
        from_newest: Annotated[
            Optional[bool],
            Query(title="Sort from newest")] = False,
):

    service = TaskService(session=session)

    return await service.get_tasks_service(
        user_id=user_id,
        task_status=task_status,
        limit=limit,
        from_newest=from_newest,
        offset=offset
    )

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

    return await service.get_task_service(task_id=task_id,user_id=user_id)

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

    return await service.update_task_service(task_id=task_id, task_update=task_update, user_id=user_id)

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
    await service.delete_task_service(task_id=task_id, user_id=user_id)

    return True

@admin_router.post("/roles", status_code=status.HTTP_201_CREATED, response_model=RoleRead)
async def create_role(
        _: Annotated[
                    User,
                    Depends(require_role("admin"))
                ],
        new_role: RoleCreate,
        session: db
):

    service = AdminService(session=session)

    return await service.create_role_service(new_role=new_role)

@admin_router.get("/roles", status_code=status.HTTP_200_OK, response_model=list[RoleRead])
async def get_roles(
        _: Annotated[
            User,
            Depends(require_role("admin"))
        ],
        session: db):

    repository = AdminRepository(session=session)
    roles = await repository.get_roles()

    return [RoleRead.model_validate(role) for role in roles]


