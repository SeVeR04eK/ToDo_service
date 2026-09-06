"""Rate limiting dependencies for FastAPI endpoints.

This module provides reusable rate limiting dependencies that can be applied
to different endpoints with different configurations and algorithms.
"""

import structlog
from typing import Optional, Literal, Callable, Awaitable
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer

from app.application.interfaces import RateLimiter
from app.infrastructure.redis.rate_limit import RedisSlidingWindowLog, RedisSlidingWindowCounter
from app.domain.exceptions import RateLimitExceededError
from app.presentation.api.dependencies.auth_dep import get_current_user
from app.domain.entities import User

logger = structlog.get_logger(__name__)
security = HTTPBearer(auto_error=False)


def get_rate_limiter(algorithm: Literal["sliding_window_log", "sliding_window_counter"]) -> RateLimiter:
    """Factory function to get the appropriate rate limiter implementation.

    Args:
        algorithm: The rate limiting algorithm to use

    Returns:
        An instance of the requested rate limiter
    """
    if algorithm == "sliding_window_log":
        return RedisSlidingWindowLog()
    elif algorithm == "sliding_window_counter":
        return RedisSlidingWindowCounter()
    else:
        raise ValueError(f"Unknown rate limiting algorithm: {algorithm}")


def rate_limit(
    key_prefix: str,
    limit: int,
    window: int,
    algorithm: Literal["sliding_window_log", "sliding_window_counter"] = "sliding_window_counter",
    fail_closed: bool = False,
    identifier_extractor: Optional[Callable[[Request], Awaitable[str]]] = None,
) -> Callable:
    """Create a rate limiting dependency for FastAPI endpoints.

    Args:
        key_prefix: Prefix for the Redis key (e.g., "login", "tasks_read")
        limit: Maximum number of requests allowed within the window
        window: Time window in seconds
        algorithm: Rate limiting algorithm to use
        fail_closed: If True, reject requests when Redis is unavailable (for security-sensitive endpoints)
        identifier_extractor: Optional async function to extract custom identifier from request

    Returns:
        A FastAPI dependency function
    """

    async def rate_limit_dependency(
        request: Request,
    ) -> None:
        """Rate limiting dependency function."""
        # Extract identifier
        if identifier_extractor:
            identifier = await identifier_extractor(request)
        else:
            # Default to IP address for unauthenticated endpoints
            identifier = request.client.host if request.client else "unknown"

        # Build Redis key
        key = f"rate_limit:{key_prefix}:{identifier}"

        # Get rate limiter
        rate_limiter = get_rate_limiter(algorithm)

        try:
            # Check if request is allowed
            allowed = await rate_limiter.is_allowed(key, limit, window)

            if not allowed:
                # Get retry-after time if available
                retry_after = await rate_limiter.get_retry_after(key, window)

                logger.warning(
                    "rate_limit_exceeded",
                    key=key,
                    identifier=identifier,
                    limit=limit,
                    window=window,
                    retry_after=retry_after,
                    algorithm=algorithm
                )

                raise RateLimitExceededError(retry_after=retry_after if retry_after else 60)

        except RateLimitExceededError:
            # Re-raise our custom exception to be handled by the exception handler
            raise
        except Exception as e:
            logger.error(
                "rate_limit_redis_error",
                key=key,
                identifier=identifier,
                error=str(e),
                fail_closed=fail_closed
            )

            if fail_closed:
                # For security-sensitive endpoints, fail closed
                raise HTTPException(
                    status_code=503,
                    detail="Service temporarily unavailable"
                )
            else:
                # For normal endpoints, fail open (skip rate limiting)
                logger.info("rate_limit_failing_open", key=key)
                return

    return rate_limit_dependency


def rate_limit_auth(
    key_prefix: str,
    limit: int,
    window: int,
    algorithm: Literal["sliding_window_log", "sliding_window_counter"] = "sliding_window_counter",
    fail_closed: bool = False,
) -> Callable:
    """Create a rate limiting dependency for authenticated endpoints.

    This version automatically uses the authenticated user's ID as the identifier.

    Args:
        key_prefix: Prefix for the Redis key (e.g., "tasks_read")
        limit: Maximum number of requests allowed within the window
        window: Time window in seconds
        algorithm: Rate limiting algorithm to use
        fail_closed: If True, reject requests when Redis is unavailable (for security-sensitive endpoints)

    Returns:
        A FastAPI dependency function that requires authentication
    """

    async def rate_limit_dependency(
        _request: Request,
        current_user: User = Depends(get_current_user),
    ) -> None:
        """Rate limiting dependency function for authenticated endpoints."""
        # Use user_id as identifier
        identifier = str(current_user.id)

        # Build Redis key
        key = f"rate_limit:{key_prefix}:{identifier}"

        # Get rate limiter
        rate_limiter = get_rate_limiter(algorithm)

        try:
            # Check if request is allowed
            allowed = await rate_limiter.is_allowed(key, limit, window)

            if not allowed:
                # Get retry-after time if available
                retry_after = await rate_limiter.get_retry_after(key, window)

                logger.warning(
                    "rate_limit_exceeded",
                    key=key,
                    identifier=identifier,
                    limit=limit,
                    window=window,
                    retry_after=retry_after,
                    algorithm=algorithm
                )

                raise RateLimitExceededError(retry_after=retry_after if retry_after else 60)

        except RateLimitExceededError:
            # Re-raise our custom exception to be handled by the exception handler
            raise
        except Exception as e:
            logger.error(
                "rate_limit_redis_error",
                key=key,
                identifier=identifier,
                error=str(e),
                fail_closed=fail_closed
            )

            if fail_closed:
                # For security-sensitive endpoints, fail closed
                raise HTTPException(
                    status_code=503,
                    detail="Service temporarily unavailable"
                )
            else:
                # For normal endpoints, fail open (skip rate limiting)
                logger.info("rate_limit_failing_open", key=key)
                return

    return rate_limit_dependency


async def extract_login_identifier(request: Request) -> str:
    """Extract identifier for login endpoint (IP + username/email).

    Args:
        request: FastAPI request object

    Returns:
        Combined identifier string
    """
    # For login, we use IP + username from form data
    ip = request.client.host if request.client else "unknown"

    # Try to get username from form data or JSON body
    username = "unknown"
    if request.method == "POST":
        # Try form data first (OAuth2PasswordRequestForm)
        form_data = await request.form()
        if "username" in form_data:
            username = form_data["username"]
        else:
            # Try JSON body
            try:
                json_data = await request.json()
                if "username" in json_data:
                    username = json_data["username"]
                elif "email" in json_data:
                    username = json_data["email"]
            except Exception:
                pass

    return f"{ip}:{username}"
