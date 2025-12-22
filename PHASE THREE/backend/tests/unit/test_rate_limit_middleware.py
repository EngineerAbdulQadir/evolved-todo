"""
Unit tests for the rate limiting middleware.
"""
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock

import pytest
from fastapi import Request, HTTPException

from app.middleware.rate_limit import RateLimiter, rate_limit_middleware


@pytest.fixture
def rate_limiter() -> RateLimiter:
    """Returns a RateLimiter instance with a small limit for testing."""
    return RateLimiter(max_requests=3, window_seconds=1)


@pytest.mark.asyncio
async def test_rate_limiter_allows_requests_below_limit(rate_limiter: RateLimiter):
    """Tests that the rate limiter allows requests below the limit."""
    user_id = "test_user"
    assert await rate_limiter.check_rate_limit(user_id) is True
    assert await rate_limiter.check_rate_limit(user_id) is True
    assert await rate_limiter.check_rate_limit(user_id) is True


@pytest.mark.asyncio
async def test_rate_limiter_denies_requests_above_limit(rate_limiter: RateLimiter):
    """Tests that the rate limiter denies requests above the limit."""
    user_id = "test_user"
    for _ in range(3):
        await rate_limiter.check_rate_limit(user_id)
    assert await rate_limiter.check_rate_limit(user_id) is False


@pytest.mark.asyncio
async def test_rate_limiter_window_resets(rate_limiter: RateLimiter):
    """Tests that the rate limiter window resets after the specified time."""
    user_id = "test_user"
    for _ in range(3):
        await rate_limiter.check_rate_limit(user_id)
    assert await rate_limiter.check_rate_limit(user_id) is False

    # Wait for the window to reset
    await asyncio.sleep(1)

    assert await rate_limiter.check_rate_limit(user_id) is True


@pytest.mark.asyncio
async def test_rate_limiter_cleanup(rate_limiter: RateLimiter):
    """Tests that the cleanup function removes old buckets."""
    user_id_1 = "test_user_1"
    user_id_2 = "test_user_2"

    await rate_limiter.check_rate_limit(user_id_1)
    # Manually set the window start time to be in the past
    rate_limiter.user_buckets[user_id_1] = (1, datetime.utcnow() - timedelta(seconds=3))
    
    await rate_limiter.check_rate_limit(user_id_2)

    await rate_limiter.cleanup_old_buckets()

    assert user_id_1 not in rate_limiter.user_buckets
    assert user_id_2 in rate_limiter.user_buckets


@pytest.mark.asyncio
async def test_rate_limit_middleware_allows_request(rate_limiter: RateLimiter):
    """Tests that the middleware allows a request and calls the next middleware."""
    request = Request({
        "type": "http",
        "state": {"user_id": "test_user"},
        "path": "/api/tasks",
        "headers": [],
    })
    call_next = AsyncMock()

    # Replace the global rate_limiter with our test instance
    from app.middleware import rate_limit
    rate_limit.rate_limiter = rate_limiter

    await rate_limit_middleware(request, call_next)

    call_next.assert_called_once()


@pytest.mark.asyncio
async def test_rate_limit_middleware_denies_request(rate_limiter: RateLimiter):
    """Tests that the middleware denies a request when the limit is exceeded."""
    request = Request({
        "type": "http",
        "state": {"user_id": "test_user"},
        "path": "/api/tasks",
        "headers": [],
    })
    call_next = AsyncMock()

    # Replace the global rate_limiter with our test instance
    from app.middleware import rate_limit
    rate_limit.rate_limiter = rate_limiter

    # Exceed the rate limit
    for _ in range(3):
        await rate_limiter.check_rate_limit("test_user")

    with pytest.raises(HTTPException) as exc_info:
        await rate_limit_middleware(request, call_next)

    assert exc_info.value.status_code == 429
    assert not call_next.called


@pytest.mark.asyncio
async def test_rate_limit_middleware_adds_headers(rate_limiter: RateLimiter):
    """Tests that the middleware adds rate limit headers to the response."""
    request = Request({
        "type": "http",
        "state": {"user_id": "test_user"},
        "path": "/api/tasks",
        "headers": [],
    })
    
    # Mock call_next to return a response-like object with a headers attribute
    response_mock = Mock()
    response_mock.headers = {}
    call_next = AsyncMock(return_value=response_mock)

    # Replace the global rate_limiter with our test instance
    from app.middleware import rate_limit
    rate_limit.rate_limiter = rate_limiter
    
    response = await rate_limit_middleware(request, call_next)
    
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert response.headers["X-RateLimit-Limit"] == "3"
    assert response.headers["X-RateLimit-Remaining"] == "2"


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/", "/health", "/api/auth/login", "/api/auth/register"])
async def test_rate_limit_middleware_skips_excluded_paths(path: str):
    """Tests that the middleware skips rate limiting for excluded paths."""
    request = Request({"type": "http", "path": path, "headers": []})
    call_next = AsyncMock()

    await rate_limit_middleware(request, call_next)

    call_next.assert_called_once()


@pytest.mark.asyncio
async def test_rate_limit_middleware_skips_unauthenticated_requests():
    """Tests that the middleware skips rate limiting for unauthenticated requests."""
    request = Request({
        "type": "http",
        "state": {},
        "path": "/api/tasks",
        "headers": [],
    })
    call_next = AsyncMock()

    await rate_limit_middleware(request, call_next)

    call_next.assert_called_once()
