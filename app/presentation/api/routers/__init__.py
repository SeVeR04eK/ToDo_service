from .auth_router import auth_router
from .user_router import user_router
from .tasks_router import tasks_router
from .admin_router import admin_router

__all__ = ["auth_router", "user_router", "tasks_router", "admin_router"]