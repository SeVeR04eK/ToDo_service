from pydantic import BaseModel, Field
from typing import Optional, Annotated


class UserPermission(BaseModel):
    is_active: Annotated[Optional[bool], Field(title="User Active Status", default=None)]
    role_id: Annotated[Optional[int], Field(title="User Role ID", default=None)]