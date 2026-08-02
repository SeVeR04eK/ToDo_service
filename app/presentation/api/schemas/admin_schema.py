from pydantic import BaseModel, Field
from typing import Optional, Annotated


class UserPermission(BaseModel):
    """Schema for admin to update user permissions (uses role name)."""
    is_active: Annotated[Optional[bool], Field(title="User Active Status", default=None)]
    role: Annotated[Optional[str], Field(title="User Role", default=None)]