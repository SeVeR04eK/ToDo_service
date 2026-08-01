from pydantic import BaseModel, Field
from typing import Optional, Annotated


class UserPermission(BaseModel):
    """Schema for admin to update user permissions (uses role name)."""
    is_active: Annotated[Optional[bool], Field(title="User Active Status", default=None)]
    role: Annotated[Optional[str], Field(title="User Role", default=None)]

class OnlyUserPermission(BaseModel):
    """Internal schema for user permission updates (uses role ID).
    
    This is used internally after resolving role name to role ID.
    """
    is_active: Annotated[Optional[bool], Field(title="User Active Status", default=None)]
    role_id: Annotated[Optional[int], Field(title="User Role ID", default=None)]