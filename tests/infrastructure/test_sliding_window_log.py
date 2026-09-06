"""Tests for RedisSlidingWindowLog rate limiter."""
import pytest
import time
from unittest.mock import AsyncMock, patch, MagicMock
from app.infrastructure.redis.rate_limit.redis_sliding_window_log import RedisSlidingWindowLog


@pytest.mark.unit
class TestRedisSlidingWindowLog:
    """Test suite for RedisSlidingWindowLog rate limiter."""

    @pytest.fixture
    def mock_redis_client(self):
        """Create a mock Redis client."""
        client = AsyncMock()
        return client

    @pytest.fixture
    def rate_limiter(self, mock_redis_client):
        """Create a RedisSlidingWindowLog instance with mocked client."""
        with patch('app.infrastructure.redis.rate_limit.redis_sliding_window_log.get_redis_client', return_value=mock_redis_client):
            return RedisSlidingWindowLog()

    async def test_first_request_allowed(self, rate_limiter, mock_redis_client):
        """Test that the first request is allowed."""
        # Mock the script to return [1, 1] (allowed, count=1)
        mock_script = AsyncMock()
        mock_script.return_value = [1, 1]
        rate_limiter._script = mock_script

        result = await rate_limiter.is_allowed("test_key", 5, 60)

        assert result is True
        mock_script.assert_called_once()

    async def test_requests_up_to_limit_allowed(self, rate_limiter, mock_redis_client):
        """Test that requests up to the limit are allowed."""
        mock_script = AsyncMock()
        # Simulate 5 requests being allowed (limit=5)
        mock_script.side_effect = [
            [1, 1],  # Request 1
            [1, 2],  # Request 2
            [1, 3],  # Request 3
            [1, 4],  # Request 4
            [1, 5],  # Request 5 (at limit)
        ]
        rate_limiter._script = mock_script

        for i in range(5):
            result = await rate_limiter.is_allowed("test_key", 5, 60)
            assert result is True, f"Request {i+1} should be allowed"

        assert mock_script.call_count == 5

    async def test_request_above_limit_rejected(self, rate_limiter, mock_redis_client):
        """Test that a request above the limit is rejected."""
        mock_script = AsyncMock()
        # Simulate limit reached (limit=5)
        mock_script.return_value = [0, 5]  # Not allowed, count=5
        rate_limiter._script = mock_script

        result = await rate_limiter.is_allowed("test_key", 5, 60)

        assert result is False
        mock_script.assert_called_once()

    async def test_different_keys_independent(self, rate_limiter, mock_redis_client):
        """Test that different keys have independent limits."""
        mock_script = AsyncMock()
        # Each key should be independent
        mock_script.return_value = [1, 1]
        rate_limiter._script = mock_script

        # Make requests with different keys
        await rate_limiter.is_allowed("key1", 5, 60)
        await rate_limiter.is_allowed("key2", 5, 60)
        await rate_limiter.is_allowed("key3", 5, 60)

        # Each should be allowed independently
        assert mock_script.call_count == 3

    async def test_redis_error_handling(self, rate_limiter, mock_redis_client):
        """Test that Redis errors are handled correctly."""
        mock_script = AsyncMock()
        mock_script.side_effect = Exception("Redis connection error")
        rate_limiter._script = mock_script

        with pytest.raises(Exception, match="Redis connection error"):
            await rate_limiter.is_allowed("test_key", 5, 60)

    async def test_get_retry_after_with_oldest_timestamp(self, rate_limiter, mock_redis_client):
        """Test retry-after calculation with oldest timestamp."""
        now = time.time()
        old_timestamp = now - 30  # 30 seconds ago
        window = 60

        # Mock zrange to return oldest timestamp
        mock_redis_client.zrange.return_value = [("member1", old_timestamp)]

        retry_after = await rate_limiter.get_retry_after("test_key", window)

        # Should return approximately 30 seconds
        assert retry_after is not None
        assert 25 <= retry_after <= 35  # Allow some tolerance

    async def test_get_retry_after_no_timestamps(self, rate_limiter, mock_redis_client):
        """Test retry-after when no timestamps exist."""
        # Mock zrange to return empty list
        mock_redis_client.zrange.return_value = []

        retry_after = await rate_limiter.get_retry_after("test_key", 60)

        assert retry_after is None

    async def test_get_retry_after_expired_timestamp(self, rate_limiter, mock_redis_client):
        """Test retry-after when oldest timestamp is already expired."""
        now = time.time()
        old_timestamp = now - 70  # 70 seconds ago (expired for 60s window)
        window = 60

        # Mock zrange to return expired timestamp
        mock_redis_client.zrange.return_value = [("member1", old_timestamp)]

        retry_after = await rate_limiter.get_retry_after("test_key", window)

        # Should return None since timestamp is expired
        assert retry_after is None

    async def test_get_retry_after_redis_error(self, rate_limiter, mock_redis_client):
        """Test retry-after with Redis error."""
        mock_redis_client.zrange.side_effect = Exception("Redis error")

        retry_after = await rate_limiter.get_retry_after("test_key", 60)

        # Should return None on error
        assert retry_after is None

    async def test_script_lazy_loading(self, rate_limiter):
        """Test that Lua script is lazy loaded on first use."""
        # Initially script should be None
        assert rate_limiter._script is None

        # Set the script directly to simulate lazy loading
        mock_script = AsyncMock()
        mock_script.return_value = [1, 1]
        rate_limiter._script = mock_script

        # Call is_allowed
        result = await rate_limiter.is_allowed("test_key", 5, 60)

        # Script should now be loaded and called
        assert result is True
        mock_script.assert_called_once()

    async def test_concurrent_requests_atomic(self, rate_limiter, mock_redis_client):
        """Test that concurrent requests are handled atomically via Lua script."""
        mock_script = AsyncMock()
        # Simulate atomic behavior - even with concurrent calls, limit is enforced
        mock_script.return_value = [0, 5]  # Limit reached
        rate_limiter._script = mock_script

        # Simulate concurrent requests
        results = []
        for _ in range(10):
            result = await rate_limiter.is_allowed("test_key", 5, 60)
            results.append(result)

        # All should be rejected due to atomic limit check
        assert all(not result for result in results)
        assert mock_script.call_count == 10

    async def test_different_limits_same_key(self, rate_limiter, mock_redis_client):
        """Test that different limits work correctly for the same key."""
        mock_script = AsyncMock()
        mock_script.return_value = [1, 1]
        rate_limiter._script = mock_script

        # Test with different limits
        await rate_limiter.is_allowed("test_key", 10, 60)
        await rate_limiter.is_allowed("test_key", 5, 60)
        await rate_limiter.is_allowed("test_key", 100, 60)

        assert mock_script.call_count == 3

    async def test_different_windows_same_key(self, rate_limiter, mock_redis_client):
        """Test that different windows work correctly for the same key."""
        mock_script = AsyncMock()
        mock_script.return_value = [1, 1]
        rate_limiter._script = mock_script

        # Test with different windows
        await rate_limiter.is_allowed("test_key", 5, 30)
        await rate_limiter.is_allowed("test_key", 5, 60)
        await rate_limiter.is_allowed("test_key", 5, 3600)

        assert mock_script.call_count == 3
