from fastapi import APIRouter, Depends, status, Path, Query, Body
from typing import Annotated, Optional, Union

from app.domain.entities import User
from app.presentation.api.schemas import UserRead, TaskRead, TaskUpdate, RoleRead, UserPermission, RoleCreate, TasksPagination, PaginatedResponse, PaginationMeta, DataResponse, ListResponse
from app.application.dto import CreateRoleDTO, UpdateTaskDTO, TaskPaginationDTO
from app.domain.enums import TaskStatus
from app.presentation.api.dependencies import require_role, tasks_pagination, rate_limit_auth
from app.application.services import AdminService
from app.presentation.api.schemas.user_schema import UserRole
from app.presentation.api.dependencies.services_dep import get_admin_service
from app.core.config import settings

# Admin router - all endpoints require admin role authentication
admin_router = APIRouter(prefix = "/admin", tags = ["admin"])

@admin_router.get("/users", status_code=status.HTTP_200_OK, response_model=Union[DataResponse[UserRead], PaginatedResponse[UserRead]], summary="Get all users", response_description="Returns a single user if username filter is provided, otherwise returns a paginated list of users")
async def get_users(
        # Underscore indicates we only need the dependency for authentication, not the actual user object
        _: Annotated[
            User,
            Depends(require_role("admin"))
        ],
        service: AdminService = Depends(get_admin_service),
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
            Query(title="Offset for pagination", ge=1, le=10000)
        ] = None,
        _rate_limit: Annotated[None, Depends(rate_limit_auth(
            key_prefix="admin_users_list",
            limit=settings.rate_limit_admin_users_list_limit,
            window=settings.rate_limit_admin_users_list_window,
            algorithm="sliding_window_counter"
        ))] = None,
) -> Union[DataResponse[UserRead], PaginatedResponse[UserRead]]:
    """
    Get all users with optional filtering by username and _pagination_:

    - **username**: Filter users by username
    - **limit**: Limit the number of users returned
    - **offset**: Offset for pagination
    """

    # Returns single UserRead if username is provided, otherwise returns PaginatedResponse[UserRead]
    result = await service.get_users_service(
        username=username,
        limit=limit,
        offset=offset
    )

    if isinstance(result, User):
        return DataResponse[UserRead](
            data=UserRead(
                id=result.id,
                username=result.username,
                is_active=result.is_active,
                role=UserRole(name=result.role.name) if result.role else None
            )
        )

    return PaginatedResponse[UserRead](
        data=[
            UserRead(
                id=user.id,
                username=user.username,
                is_active=user.is_active,
                role=UserRole(name=user.role.name) if user.role else None
            )
            for user in result.items
        ],
        meta=PaginationMeta(
            page=result.page,
            page_size=result.page_size,
            total_items=result.total_items,
            total_pages=result.total_pages,
            has_next=result.has_next,
            has_previous=result.has_previous
        )
    )

@admin_router.get("/users/{user_id}", status_code=status.HTTP_200_OK, response_model=DataResponse[UserRead], summary="Get specific user")
async def get_user(
        _: Annotated[
                    User,
                    Depends(require_role("admin"))
                ],
        user_id: Annotated[int, Path(..., title="User ID")],
        service: AdminService = Depends(get_admin_service),
        _rate_limit: Annotated[None, Depends(rate_limit_auth(
            key_prefix="admin_users_get",
            limit=settings.rate_limit_admin_users_get_limit,
            window=settings.rate_limit_admin_users_get_window,
            algorithm="sliding_window_counter"
        ))] = None,
) -> DataResponse[UserRead]:
    """Get a specific user by ID."""

    user = await service.get_user_service(user_id)
    return DataResponse[UserRead](
        data=UserRead(
            id=user.id,
            username=user.username,
            is_active=user.is_active,
            role=UserRole(name=user.role.name) if user.role else None
        )
    )

@admin_router.patch("/users/{user_id}", status_code=status.HTTP_200_OK, response_model=DataResponse[UserRead], summary="Update user permissions")
async def user_permission(
        _: Annotated[
                    User,
                    Depends(require_role("admin"))
                ],
        user_id: Annotated[int, Path(..., title="User ID")],
        user_perm: Annotated[
            UserPermission,
            Body(
                openapi_examples={
                    "full": {
                        "summary": "Update user permissions with all fields.",
                        "description": "Update user profile with all fields: is_active, role",
                        "value": {
                            "is_active": False,
                            "role": "admin"
                        }
                    },
                    "partial_is_active": {
                        "summary": "Update user profile with only the provided is_active field.",
                        "description": "Update user profile with only the provided field: is_active",
                        "value": {
                            "is_active": False
                        }
                    },
                    "partial_role": {
                        "summary": "Update user profile with only the provided role.",
                        "description": "Update user profile with only the provided field: role",
                        "value": {
                            "role": "admin"
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
        service: AdminService = Depends(get_admin_service),
        _rate_limit: Annotated[None, Depends(rate_limit_auth(
            key_prefix="admin_users_patch",
            limit=settings.rate_limit_admin_users_patch_limit,
            window=settings.rate_limit_admin_users_patch_window,
            algorithm="sliding_window_counter"
        ))] = None,
) -> DataResponse[UserRead]:
    """Update user permissions (_Partial update_)."""

    user = await service.permission_user_service(user_id=user_id, role_name=user_perm.role, is_active=user_perm.is_active)
    return DataResponse[UserRead](
        data=UserRead(
            id=user.id,
            username=user.username,
            is_active=user.is_active,
            role=UserRole(name=user.role.name) if user.role else None
        )
    )

@admin_router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete user")
async def delete_user(
        _: Annotated[
                    User,
                    Depends(require_role("admin"))
                ],
        user_id: Annotated[int, Path(..., title="User ID")],
        service: AdminService = Depends(get_admin_service),
        _rate_limit: Annotated[None, Depends(rate_limit_auth(
            key_prefix="admin_users_delete",
            limit=settings.rate_limit_admin_users_delete_limit,
            window=settings.rate_limit_admin_users_delete_window,
            algorithm="sliding_window_counter"
        ))] = None,
) -> None:
    """Delete a specific user by ID."""

    await service.delete_user_service(user_id)

@admin_router.get("/users/{user_id}/tasks", status_code=status.HTTP_200_OK, response_model=PaginatedResponse[TaskRead], summary="Get user tasks")
async def get_tasks(
        _: Annotated[
                    User,
                    Depends(require_role("admin"))
                ],
        user_id: Annotated[int, Path(..., title="User ID")],
        service: AdminService = Depends(get_admin_service),
        task_status: Annotated[
            Optional[TaskStatus],
            Query(title="Task Status")
        ] = None,
        pagination: TasksPagination = Depends(tasks_pagination),
        _rate_limit: Annotated[None, Depends(rate_limit_auth(
            key_prefix="admin_user_tasks_list",
            limit=settings.rate_limit_admin_user_tasks_list_limit,
            window=settings.rate_limit_admin_user_tasks_list_window,
            algorithm="sliding_window_counter"
        ))] = None,
) -> PaginatedResponse[TaskRead]:
    """Get tasks for a specific user by ID with optional _filtering_ and _pagination_:
    - **task_status**: Filter tasks by status
    - **limit**: Limit the number of tasks returned
    - **offset**: Offset for pagination
    - **from_newest**: Boolean to sort tasks from the newest first
    """

    pagination = TaskPaginationDTO(
        limit=pagination.limit,
        offset=pagination.offset,
        from_newest=pagination.from_newest
    )

    page = await service.get_tasks_service(
        user_id=user_id,
        task_status=task_status,
        pagination=pagination
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

@admin_router.get("/users/{user_id}/tasks/{task_id}", status_code=status.HTTP_200_OK, response_model=DataResponse[TaskRead], summary="Get specific user task")
async def get_task(
        _: Annotated[
                    User,
                    Depends(require_role("admin"))
                ],
        user_id: Annotated[int, Path(..., title="User ID")],
        task_id: Annotated[int, Path(..., title="Task ID")],
        service: AdminService = Depends(get_admin_service),
        _rate_limit: Annotated[None, Depends(rate_limit_auth(
            key_prefix="admin_user_task_get",
            limit=settings.rate_limit_admin_user_task_get_limit,
            window=settings.rate_limit_admin_user_task_get_window,
            algorithm="sliding_window_counter"
        ))] = None,
) -> DataResponse[TaskRead]:
    """Get a specific task for a user by ID."""

    task = await service.get_task_service(task_id=task_id, user_id=user_id)
    return DataResponse[TaskRead](
        data=TaskRead(
            id=task.id,
            title=task.title,
            content=task.content,
            status=task.status,
            user_id=task.user_id
        )
    )

@admin_router.patch("/users/{user_id}/tasks/{task_id}", status_code=status.HTTP_200_OK, response_model=DataResponse[TaskRead], summary="Update user task")
async def update_task(
        _: Annotated[
                    User,
                    Depends(require_role("admin"))
                ],
        task_id: Annotated[int, Path(..., title="Task ID")],
        user_id: Annotated[int, Path(..., title="User ID")],
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
                    "partial_сontent": {
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
        service: AdminService = Depends(get_admin_service),
        _rate_limit: Annotated[None, Depends(rate_limit_auth(
            key_prefix="admin_user_task_update",
            limit=settings.rate_limit_admin_user_task_update_limit,
            window=settings.rate_limit_admin_user_task_update_window,
            algorithm="sliding_window_counter"
        ))] = None,
) -> DataResponse[TaskRead]:
    """Update a specific task for a user by ID (_Partial update_")."""

    task_dto = UpdateTaskDTO(
        title=task_update.title,
        content=task_update.content,
        status=task_update.status
    )

    task = await service.update_task_service(task_id=task_id, user_id=user_id, task_update=task_dto)

    return DataResponse[TaskRead](
        data=TaskRead(
            id=task.id,
            title=task.title,
            content=task.content,
            status=task.status,
            user_id=task.user_id
        )
    )

@admin_router.delete("/users/{user_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete user task")
async def delete_task(
        _: Annotated[
                    User,
                    Depends(require_role("admin"))
                ],
        task_id: Annotated[int, Path(..., title="Task ID")],
        user_id: Annotated[int, Path(..., title="User ID")],
        service: AdminService = Depends(get_admin_service),
        _rate_limit: Annotated[None, Depends(rate_limit_auth(
            key_prefix="admin_user_task_delete",
            limit=settings.rate_limit_admin_user_task_delete_limit,
            window=settings.rate_limit_admin_user_task_delete_window,
            algorithm="sliding_window_counter"
        ))] = None,
) -> None:
    """Delete a specific task for a user by ID."""

    await service.delete_task_service(task_id=task_id, user_id=user_id)

@admin_router.post("/roles", status_code=status.HTTP_201_CREATED, response_model=DataResponse[RoleRead], summary="Create new role")
async def create_role(
        _: Annotated[
                    User,
                    Depends(require_role("admin"))
                ],
        new_role: RoleCreate,
        service: AdminService = Depends(get_admin_service),
        _rate_limit: Annotated[None, Depends(rate_limit_auth(
            key_prefix="admin_role_create",
            limit=settings.rate_limit_admin_role_create_limit,
            window=settings.rate_limit_admin_role_create_window,
            algorithm="sliding_window_counter"
        ))] = None,
) -> DataResponse[RoleRead]:
    """Create a new role."""

    role_dto = CreateRoleDTO(name=new_role.name)

    role = await service.create_role_service(new_role=role_dto)

    return DataResponse[RoleRead](
        data=RoleRead(
            id=role.id,
            name=role.name
        )
    )

@admin_router.get("/roles", status_code=status.HTTP_200_OK, response_model=ListResponse[RoleRead])
async def get_roles(
        _: Annotated[
            User,
            Depends(require_role("admin"))
        ],
        service: AdminService = Depends(get_admin_service),
        _rate_limit: Annotated[None, Depends(rate_limit_auth(
            key_prefix="admin_roles_list",
            limit=settings.rate_limit_admin_roles_list_limit,
            window=settings.rate_limit_admin_roles_list_window,
            algorithm="sliding_window_counter"
        ))] = None,
) -> ListResponse[RoleRead]:
    roles = await service.get_roles_service()
    return ListResponse[RoleRead](
        data=[
            RoleRead(
                id=role.id,
                name=role.name
            )
            for role in roles
        ]
    )


