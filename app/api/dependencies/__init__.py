"""
API dependency exports.

This module exports common dependencies used across API routers:
- db: Database session dependency
- get_current_user: Authentication dependency to get current user
- require_role: Role-based access control dependency
"""
from .auth_dep import db, get_current_user
from .rbac import require_role
from .pagination import tasks_pagination

__all__ = ["db", "get_current_user", "require_role", "tasks_pagination"]
