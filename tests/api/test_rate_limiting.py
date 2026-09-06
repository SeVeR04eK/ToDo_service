"""Integration tests for rate limiting on API endpoints."""
import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient

from app.main import app
from app.domain.exceptions import RateLimitExceededError
from app.application.interfaces import RateLimiter


@pytest.mark.integration
class TestRateLimitingIntegration:
    """Integration tests for rate limiting on API endpoints."""

    @pytest.fixture
    def mock_rate_limiter(self):
        """Create a mock rate limiter."""
        limiter = AsyncMock(spec=RateLimiter)
        return limiter

    @pytest.fixture
    async def client_with_mock_rate_limiter(self, mock_rate_limiter, db_session):
        """Create test client with mocked rate limiter and database session."""
        from app.infrastructure.redis.rate_limit import RedisSlidingWindowLog, RedisSlidingWindowCounter
        from app.infrastructure.repositories import SQLAlchemyUserRepository, SQLAlchemyTaskRepository, SQLAlchemyRefreshTokenRepository, SQLAlchemyAdminRepository
        from app.infrastructure.unit_of_work import SQLAlchemyUnitOfWork
        from app.infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher
        from app.infrastructure.security.sha256_token_hasher import SHA256TokenHasher
        from app.presentation.api.dependencies.repositories_dep import get_user_repository, get_task_repository, get_refresh_token_repository, get_admin_repository
        from app.presentation.api.dependencies.uow import get_unit_of_work
        from app.presentation.api.dependencies.token_hasher_dep import get_token_hasher
        from app.presentation.api.dependencies.cache_dep import get_user_cache, get_task_cache, get_role_cache
        from app.presentation.api.dependencies.auth_dep import get_current_user
        from app.domain.entities import User, Role
        from app.infrastructure.database import get_session
        from app.application.interfaces import UserCache, TaskCache, RoleCache
        from unittest.mock import AsyncMock, patch
        from httpx import ASGITransport

        password_hasher = BcryptPasswordHasher()
        token_hasher = SHA256TokenHasher()

        # Mock caches
        mock_user_cache = AsyncMock(spec=UserCache)
        mock_user_cache.get_user.return_value = None
        mock_task_cache = AsyncMock(spec=TaskCache)
        mock_task_cache.get_task.return_value = None
        mock_task_cache.get_task_list.return_value = None
        mock_role_cache = AsyncMock(spec=RoleCache)
        mock_role_cache.get_roles.return_value = None

        async def override_get_session():
            yield db_session

        async def override_get_user_repository():
            yield SQLAlchemyUserRepository(db_session, password_hasher)

        async def override_get_task_repository():
            yield SQLAlchemyTaskRepository(db_session)

        async def override_get_refresh_token_repository():
            yield SQLAlchemyRefreshTokenRepository(db_session)

        async def override_get_admin_repository():
            yield SQLAlchemyAdminRepository(db_session)

        async def override_get_unit_of_work():
            yield SQLAlchemyUnitOfWork(db_session, password_hasher)

        async def override_get_token_hasher():
            yield token_hasher

        async def override_get_user_cache():
            yield mock_user_cache

        async def override_get_task_cache():
            yield mock_task_cache

        async def override_get_role_cache():
            yield mock_role_cache

        app.dependency_overrides[get_session] = override_get_session
        app.dependency_overrides[get_user_repository] = override_get_user_repository
        app.dependency_overrides[get_task_repository] = override_get_task_repository
        app.dependency_overrides[get_refresh_token_repository] = override_get_refresh_token_repository
        app.dependency_overrides[get_admin_repository] = override_get_admin_repository
        app.dependency_overrides[get_unit_of_work] = override_get_unit_of_work
        app.dependency_overrides[get_token_hasher] = override_get_token_hasher
        app.dependency_overrides[get_user_cache] = override_get_user_cache
        app.dependency_overrides[get_task_cache] = override_get_task_cache
        app.dependency_overrides[get_role_cache] = override_get_role_cache

        # Patch the Redis rate limiter classes
        with patch.object(RedisSlidingWindowLog, '__init__', return_value=None):
            with patch.object(RedisSlidingWindowLog, 'is_allowed', mock_rate_limiter.is_allowed):
                with patch.object(RedisSlidingWindowLog, 'get_retry_after', mock_rate_limiter.get_retry_after):
                    with patch.object(RedisSlidingWindowCounter, '__init__', return_value=None):
                        with patch.object(RedisSlidingWindowCounter, 'is_allowed', mock_rate_limiter.is_allowed):
                            with patch.object(RedisSlidingWindowCounter, 'get_retry_after', mock_rate_limiter.get_retry_after):
                                async with AsyncClient(
                                    transport=ASGITransport(app=app),
                                    base_url="http://test"
                                ) as ac:
                                    yield ac

        app.dependency_overrides.clear()

    async def test_login_rate_limit_allowed(self, client_with_mock_rate_limiter, mock_rate_limiter):
        """Test that login requests are allowed under the limit."""
        # Mock rate limiter to allow requests
        mock_rate_limiter.is_allowed.return_value = True
        mock_rate_limiter.get_retry_after.return_value = None

        response = await client_with_mock_rate_limiter.post(
            "/auth/authentication",
            data={"username": "testuser", "password": "testpass"}
        )

        # The request should proceed (may fail auth, but rate limit should pass)
        # We're testing that rate limiting doesn't block when allowed
        assert response.status_code in [200, 401]  # 200 if auth succeeds, 401 if it fails
        mock_rate_limiter.is_allowed.assert_called_once()

    async def test_login_rate_limit_exceeded(self, client_with_mock_rate_limiter, mock_rate_limiter):
        """Test that login requests are rejected when limit is exceeded."""
        # Mock rate limiter to reject requests
        mock_rate_limiter.is_allowed.return_value = False
        mock_rate_limiter.get_retry_after.return_value = 60

        response = await client_with_mock_rate_limiter.post(
            "/auth/authentication",
            data={"username": "testuser", "password": "testpass"}
        )

        # Should return 429 for rate limit exceeded
        assert response.status_code == 429
        assert response.json()["code"] == "RATE_LIMIT_EXCEEDED"
        assert "Retry-After" in response.headers
        mock_rate_limiter.is_allowed.assert_called_once()

    async def test_login_identifier_extraction(self, client_with_mock_rate_limiter, mock_rate_limiter):
        """Test that login endpoint uses IP + username as identifier."""
        mock_rate_limiter.is_allowed.return_value = True

        response = await client_with_mock_rate_limiter.post(
            "/auth/authentication",
            data={"username": "testuser", "password": "testpass"}
        )

        # Check that rate limiter was called with correct key format
        mock_rate_limiter.is_allowed.assert_called_once()
        call_args = mock_rate_limiter.is_allowed.call_args
        key = call_args[0][0]  # First positional argument is the key
        # Key should contain "login" and the identifier
        assert "login" in key
        assert "testuser" in key or "unknown" in key

    async def test_refresh_rate_limit_allowed(self, client_with_mock_rate_limiter, mock_rate_limiter):
        """Test that refresh requests are allowed under the limit."""
        mock_rate_limiter.is_allowed.return_value = True

        response = await client_with_mock_rate_limiter.post(
            "/auth/refresh",
            json={"refresh_token": "test_token"}
        )

        # Rate limit should not block
        assert response.status_code in [200, 401]  # May fail auth but rate limit passes
        mock_rate_limiter.is_allowed.assert_called_once()

    async def test_refresh_rate_limit_exceeded(self, client_with_mock_rate_limiter, mock_rate_limiter):
        """Test that refresh requests are rejected when limit is exceeded."""
        mock_rate_limiter.is_allowed.return_value = False
        mock_rate_limiter.get_retry_after.return_value = 60

        response = await client_with_mock_rate_limiter.post(
            "/auth/refresh",
            json={"refresh_token": "test_token"}
        )

        assert response.status_code == 429
        assert response.json()["code"] == "RATE_LIMIT_EXCEEDED"

    async def test_authenticated_endpoint_rate_limit(self, client_with_mock_rate_limiter, mock_rate_limiter):
        """Test that authenticated endpoints use user_id as identifier."""
        mock_rate_limiter.is_allowed.return_value = True

        # Mock the authentication dependency to return a user
        from app.domain.entities import User, Role
        from app.presentation.api.dependencies.auth_dep import get_current_user

        test_role = Role(id=1, name="user")
        test_user = User(
            id=123,
            username="testuser",
            is_active=True,
            hashed_password="hashed",
            role_id=1,
            role=test_role
        )

        async def override_get_current_user():
            return test_user

        app.dependency_overrides[get_current_user] = override_get_current_user

        response = await client_with_mock_rate_limiter.get(
            "/user/me",
            headers={"Authorization": "Bearer fake_token"}
        )

        # Check that rate limiter was called with user_id in key
        mock_rate_limiter.is_allowed.assert_called_once()
        call_args = mock_rate_limiter.is_allowed.call_args
        key = call_args[0][0]
        assert "123" in key  # user_id should be in the key

        app.dependency_overrides.clear()

    async def test_different_users_independent_limits(self, client_with_mock_rate_limiter, mock_rate_limiter):
        """Test that different users have independent rate limits."""
        mock_rate_limiter.is_allowed.return_value = True

        from app.domain.entities import User, Role
        from app.presentation.api.dependencies.auth_dep import get_current_user

        # Test with user 1
        role1 = Role(id=1, name="user")
        user1 = User(id=1, username="user1", is_active=True, hashed_password="hashed", role_id=1, role=role1)
        async def override_get_user1():
            return user1

        app.dependency_overrides[get_current_user] = override_get_user1

        response1 = await client_with_mock_rate_limiter.get(
            "/user/me",
            headers={"Authorization": "Bearer fake_token"}
        )

        key1 = mock_rate_limiter.is_allowed.call_args[0][0]

        # Test with user 2
        role2 = Role(id=1, name="user")
        user2 = User(id=2, username="user2", is_active=True, hashed_password="hashed", role_id=1, role=role2)
        async def override_get_user2():
            return user2

        app.dependency_overrides[get_current_user] = override_get_user2

        response2 = await client_with_mock_rate_limiter.get(
            "/user/me",
            headers={"Authorization": "Bearer fake_token"}
        )

        key2 = mock_rate_limiter.is_allowed.call_args[0][0]

        # Keys should be different (different user_ids)
        assert key1 != key2
        assert "1" in key1
        assert "2" in key2

        app.dependency_overrides.clear()

    async def test_rate_limit_retry_after_header(self, client_with_mock_rate_limiter, mock_rate_limiter):
        """Test that Retry-After header is included when limit is exceeded."""
        mock_rate_limiter.is_allowed.return_value = False
        mock_rate_limiter.get_retry_after.return_value = 45

        response = await client_with_mock_rate_limiter.post(
            "/auth/authentication",
            data={"username": "testuser", "password": "testpass"}
        )

        assert response.status_code == 429
        assert "Retry-After" in response.headers
        # The header should be set to the value returned by get_retry_after
        assert response.headers["Retry-After"] == "45"

    async def test_health_endpoint_no_rate_limit(self, client_with_mock_rate_limiter, mock_rate_limiter):
        """Test that health endpoint is not rate limited."""
        response = await client_with_mock_rate_limiter.get("/health/")

        # Health endpoint should not have rate limiting
        assert response.status_code == 200
        # Rate limiter should not be called
        mock_rate_limiter.is_allowed.assert_not_called()

    async def test_rate_limit_redis_error_fail_open(self, client_with_mock_rate_limiter, mock_rate_limiter):
        """Test that Redis errors fail open for non-critical endpoints."""
        mock_rate_limiter.is_allowed.side_effect = Exception("Redis error")

        response = await client_with_mock_rate_limiter.post(
            "/auth/refresh",
            json={"refresh_token": "test_token"}
        )

        # Should fail open - request proceeds despite Redis error
        # (May fail auth, but rate limiting shouldn't block)
        assert response.status_code in [200, 401]

    async def test_rate_limit_redis_error_fail_closed(self, client_with_mock_rate_limiter, mock_rate_limiter):
        """Test that Redis errors fail closed for critical endpoints like login."""
        mock_rate_limiter.is_allowed.side_effect = Exception("Redis error")

        response = await client_with_mock_rate_limiter.post(
            "/auth/authentication",
            data={"username": "testuser", "password": "testpass"}
        )

        # Should fail closed - request is rejected with 503
        assert response.status_code == 503

    async def test_task_endpoint_rate_limit(self, client_with_mock_rate_limiter, mock_rate_limiter):
        """Test that task endpoints are rate limited."""
        mock_rate_limiter.is_allowed.return_value = True

        from app.domain.entities import User, Role
        from app.presentation.api.dependencies.auth_dep import get_current_user

        test_role = Role(id=1, name="user")
        test_user = User(id=123, username="testuser", is_active=True, hashed_password="hashed", role_id=1, role=test_role)
        async def override_get_current_user():
            return test_user

        app.dependency_overrides[get_current_user] = override_get_current_user

        response = await client_with_mock_rate_limiter.get(
            "/tasks/me",
            headers={"Authorization": "Bearer fake_token"}
        )

        # Rate limiter should be called
        mock_rate_limiter.is_allowed.assert_called_once()
        key = mock_rate_limiter.is_allowed.call_args[0][0]
        assert "tasks_read" in key
        assert "123" in key

        app.dependency_overrides.clear()

    async def test_admin_endpoint_rate_limit(self, client_with_mock_rate_limiter, mock_rate_limiter):
        """Test that admin endpoints are rate limited."""
        mock_rate_limiter.is_allowed.return_value = True

        from app.domain.entities import User, Role
        from app.presentation.api.dependencies.auth_dep import get_current_user

        test_role = Role(id=1, name="admin")
        test_user = User(id=123, username="admin", is_active=True, hashed_password="hashed", role_id=1, role=test_role)
        async def override_get_current_user():
            return test_user

        app.dependency_overrides[get_current_user] = override_get_current_user

        response = await client_with_mock_rate_limiter.get(
            "/admin/users",
            headers={"Authorization": "Bearer fake_token"}
        )

        # Rate limiter should be called
        mock_rate_limiter.is_allowed.assert_called_once()
        key = mock_rate_limiter.is_allowed.call_args[0][0]
        assert "admin_users_list" in key
        assert "123" in key

        app.dependency_overrides.clear()
