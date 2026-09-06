from app.application.interfaces import UserCache, TaskCache, RoleCache
from app.infrastructure.redis.cache import RedisUserCache, RedisTaskCache, RedisRoleCache


def get_user_cache() -> UserCache:
    return RedisUserCache()


def get_task_cache() -> TaskCache:
    return RedisTaskCache()


def get_role_cache() -> RoleCache:
    return RedisRoleCache()
