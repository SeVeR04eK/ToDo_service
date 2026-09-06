"""
API dependency exports.

This module exports common dependencies used across API routers:
- get_current_user: Authentication dependency to get current user
- require_role: Role-based access control dependency
- rate_limit: Rate limiting dependency for unauthenticated endpoints
- rate_limit_auth: Rate limiting dependency for authenticated endpoints
"""
from .auth_dep import get_current_user
from .rbac import require_role
from .pagination import tasks_pagination
from .rate_limit_dep import rate_limit, rate_limit_auth, extract_login_identifier

__all__ = ["get_current_user", "require_role", "tasks_pagination", "rate_limit", "rate_limit_auth", "extract_login_identifier"]
