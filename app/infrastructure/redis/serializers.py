"""Serialization utilities for Redis cache.

This module provides functions to serialize and deserialize domain entities
to/from JSON for storage in Redis.
"""

import json
from typing import Any, Dict, List

from app.domain.entities import User, Role, Task
from app.domain.enums import TaskStatus
from app.domain.exceptions import SerializationError


def serialize_user(user: User) -> Dict[str, Any]:
    """Serialize User entity to dictionary for JSON storage."""
    return {
        "id": user.id,
        "username": user.username,
        "hashed_password": user.hashed_password,
        "is_active": user.is_active,
        "role_id": user.role_id,
        "role": serialize_role(user.role) if user.role else None
    }


def deserialize_user(data: Dict[str, Any]) -> User:
    """Deserialize dictionary to User entity."""
    if data.get("role"):
        data["role"] = deserialize_role(data["role"])
    return User(**data)


def serialize_role(role: Role) -> Dict[str, Any]:
    """Serialize Role entity to dictionary for JSON storage."""
    return {
        "id": role.id,
        "name": role.name
    }


def deserialize_role(data: Dict[str, Any]) -> Role:
    """Deserialize dictionary to Role entity."""
    return Role(**data)


def serialize_task(task: Task) -> Dict[str, Any]:
    """Serialize Task entity to dictionary for JSON storage."""
    return {
        "id": task.id,
        "title": task.title,
        "content": task.content,
        "status": task.status.value,  # Store enum as string
        "user_id": task.user_id
    }


def deserialize_task(data: Dict[str, Any]) -> Task:
    """Deserialize dictionary to Task entity."""
    # Convert status string back to TaskStatus enum
    if "status" in data:
        data["status"] = TaskStatus(data["status"])
    return Task(**data)


def serialize_task_list(tasks: List[Task], page_metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Serialize a list of tasks with pagination metadata."""
    return {
        "items": [serialize_task(task) for task in tasks],
        **page_metadata
    }


def deserialize_task_list(data: Dict[str, Any]) -> tuple[List[Task], Dict[str, Any]]:
    """Deserialize a list of tasks with pagination metadata."""
    tasks = [deserialize_task(task_data) for task_data in data["items"]]
    page_metadata = {k: v for k, v in data.items() if k != "items"}
    return tasks, page_metadata


def serialize_roles(roles: List[Role]) -> List[Dict[str, Any]]:
    """Serialize a list of Role entities."""
    return [serialize_role(role) for role in roles]


def deserialize_roles(data: List[Dict[str, Any]]) -> List[Role]:
    """Deserialize a list of Role entities."""
    return [deserialize_role(role_data) for role_data in data]


def to_json(obj: Any) -> str:
    """Convert object to JSON string."""
    try:
        return json.dumps(obj)
    except (TypeError, ValueError):
        raise SerializationError()


def from_json(json_str: str) -> Any:
    """Parse JSON string to object."""
    try:
        return json.loads(json_str)
    except (TypeError, ValueError):
        raise SerializationError()
