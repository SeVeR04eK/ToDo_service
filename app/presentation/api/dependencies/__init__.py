"""
API dependency exports.

This module exports common dependencies used across API routers:
- get_current_user: Authentication dependency to get current user
- require_role: Role-based access control dependency
"""
from .auth_dep import get_current_user
from .rbac import require_role
from .pagination import tasks_pagination

__all__ = ["get_current_user", "require_role", "tasks_pagination"]
