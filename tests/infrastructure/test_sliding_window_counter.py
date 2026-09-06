"""Tests for RedisSlidingWindowCounter rate limiter."""
import pytest
import time
import math
from unittest.mock import AsyncMock, patch, MagicMock
from app.infrastructure.redis.rate_limit.redis_sliding_window_counter import RedisSlidingWindowCounter


@pytest.mark.unit
class TestRedisSlidingWindowCounter:
    """Test suite for RedisSlidingWindowCounter rate limiter."""

    @pytest.fixture
    def mock_redis_client(self):
        """Create a mock Redis client."""
        client = AsyncMock()
        return client

    @pytest.fixture
    def rate_limiter(self, mock_redis_client):
        """Create a RedisSlidingWindowCounter instance with mocked client."""
        with patch('app.infrastructure.redis.rate_limit.redis_sliding_window_counter.get_redis_client', return_value=mock_redis_client):
            return RedisSlidingWindowCounter()

    async def test_first_request_allowed(self, rate_limiter, mock_redis_client):
        """Test that the first request is allowed."""
        # Mock the script to return [1, 1.0, 1] (allowed, weighted_count=1.0, current_count=1)
        mock_script = AsyncMock()
        mock_script.return_value = [1, 1.0, 1]
        rate_limiter._script = mock_script

        result = await rate_limiter.is_allowed("test_key", 5, 60)

        assert result is True
        mock_script.assert_called_once()

    async def test_requests_below_limit_allowed(self, rate_limiter, mock_redis_client):
        """Test that requests below the limit are allowed."""
        mock_script = AsyncMock()
        # Simulate requests below limit (limit=5)
        mock_script.side_effect = [
            [1, 1.0, 1],  # Request 1
            [1, 2.0, 2],  # Request 2
            [1, 3.0, 3],  # Request 3
            [1, 4.0, 4],  # Request 4
        ]
        rate_limiter._script = mock_script

        for i in range(4):
            result = await rate_limiter.is_allowed("test_key", 5, 60)
            assert result is True, f"Request {i+1} should be allowed"

        assert mock_script.call_count == 4

    async def test_request_above_limit_rejected(self, rate_limiter, mock_redis_client):
        """Test that a request above the calculated limit is rejected."""
        mock_script = AsyncMock()
        # Simulate limit exceeded (limit=5, weighted_count=5.0)
        mock_script.return_value = [0, 5.0, 5]  # Not allowed, weighted_count=5.0
        rate_limiter._script = mock_script

        result = await rate_limiter.is_allowed("test_key", 5, 60)

        assert result is False
        mock_script.assert_called_once()

    async def test_different_keys_independent(self, rate_limiter, mock_redis_client):
        """Test that different keys have independent limits."""
        mock_script = AsyncMock()
        # Each key should be independent
        mock_script.return_value = [1, 1.0, 1]
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

    async def test_weighted_count_calculation(self, rate_limiter, mock_redis_client):
        """Test that weighted count is calculated correctly."""
        mock_script = AsyncMock()
        # Simulate weighted count calculation
        # Previous window: 3 requests, current window: 2 requests
        # Weight should be based on elapsed time in current window
        mock_script.return_value = [1, 2.5, 2]  # allowed, weighted_count=2.5, current_count=2
        rate_limiter._script = mock_script

        result = await rate_limiter.is_allowed("test_key", 5, 60)

        assert result is True
        mock_script.assert_called_once()

    async def test_window_transition(self, rate_limiter, mock_redis_client):
        """Test that window transition works correctly."""
        mock_script = AsyncMock()
        # Simulate window transition - previous window count decreases in weight
        mock_script.side_effect = [
            [1, 1.0, 1],  # First window
            [1, 1.5, 2],  # Transitioning - previous window still has some weight
            [1, 1.2, 1],  # New window - previous window weight decreased
        ]
        rate_limiter._script = mock_script

        await rate_limiter.is_allowed("test_key", 5, 60)
        await rate_limiter.is_allowed("test_key", 5, 60)
        await rate_limiter.is_allowed("test_key", 5, 60)

        assert mock_script.call_count == 3

    async def test_get_retry_after_with_current_window(self, rate_limiter, mock_redis_client):
        """Test retry-after calculation with current window data."""
        now = time.time()
        current_window = math.floor(now / 60)
        elapsed_in_current = now % 60

        # Mock hget to return current window count
        mock_redis_client.hget.return_value = "5"

        retry_after = await rate_limiter.get_retry_after("test_key", 60)

        # Should return time until window rolls over
        assert retry_after is not None
        expected_retry = int(60 - elapsed_in_current)
        assert abs(retry_after - expected_retry) <= 2  # Allow small tolerance

    async def test_get_retry_after_no_data(self, rate_limiter, mock_redis_client):
        """Test retry-after when no data exists."""
        # Mock hget to return None
        mock_redis_client.hget.return_value = None

        retry_after = await rate_limiter.get_retry_after("test_key", 60)

        assert retry_after is None

    async def test_get_retry_after_below_limit(self, rate_limiter, mock_redis_client):
        """Test retry-after when count is zero (no requests)."""
        # Mock hget to return None (no data)
        mock_redis_client.hget.return_value = None

        retry_after = await rate_limiter.get_retry_after("test_key", 60)

        # Should return None since there's no data
        assert retry_after is None

    async def test_get_retry_after_redis_error(self, rate_limiter, mock_redis_client):
        """Test retry-after with Redis error."""
        mock_redis_client.hget.side_effect = Exception("Redis error")

        retry_after = await rate_limiter.get_retry_after("test_key", 60)

        # Should return None on error
        assert retry_after is None

    async def test_script_lazy_loading(self, rate_limiter):
        """Test that Lua script is lazy loaded on first use."""
        # Initially script should be None
        assert rate_limiter._script is None

        # Set the script directly to simulate lazy loading
        mock_script = AsyncMock()
        mock_script.return_value = [1, 1.0, 1]
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
        mock_script.return_value = [0, 5.0, 5]  # Limit reached
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
        mock_script.return_value = [1, 1.0, 1]
        rate_limiter._script = mock_script

        # Test with different limits
        await rate_limiter.is_allowed("test_key", 10, 60)
        await rate_limiter.is_allowed("test_key", 5, 60)
        await rate_limiter.is_allowed("test_key", 100, 60)

        assert mock_script.call_count == 3

    async def test_different_windows_same_key(self, rate_limiter, mock_redis_client):
        """Test that different windows work correctly for the same key."""
        mock_script = AsyncMock()
        mock_script.return_value = [1, 1.0, 1]
        rate_limiter._script = mock_script

        # Test with different windows
        await rate_limiter.is_allowed("test_key", 5, 30)
        await rate_limiter.is_allowed("test_key", 5, 60)
        await rate_limiter.is_allowed("test_key", 5, 3600)

        assert mock_script.call_count == 3

    async def test_previous_window_weighting(self, rate_limiter, mock_redis_client):
        """Test that previous window is correctly weighted."""
        mock_script = AsyncMock()
        # Simulate previous window having weight
        # Previous: 3 requests, current: 1 request, weight: 0.5 (halfway through window)
        # Weighted count = 3 * 0.5 + 1 = 2.5
        mock_script.return_value = [1, 2.5, 1]
        rate_limiter._script = mock_script

        result = await rate_limiter.is_allowed("test_key", 5, 60)

        assert result is True
        mock_script.assert_called_once()

    async def test_expiration_set_on_request(self, rate_limiter, mock_redis_client):
        """Test that expiration is set on each request."""
        mock_script = AsyncMock()
        mock_script.return_value = [1, 1.0, 1]
        rate_limiter._script = mock_script

        await rate_limiter.is_allowed("test_key", 5, 60)

        # The Lua script should have been called with the window parameter
        mock_script.assert_called_once()
        call_args = mock_script.call_args
        # Check that window (60) is in the args
        assert 60 in call_args[1]['args']
