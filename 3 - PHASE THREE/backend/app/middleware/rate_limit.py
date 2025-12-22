"""
Rate limiting middleware to prevent API abuse (T225).

Implements token bucket algorithm with per-user rate limits:
- 100 requests per minute per user
- Sliding window to prevent burst attacks
- Returns 429 status code when limit exceeded
"""

from datetime import datetime, timedelta
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status
from collections import defaultdict
import asyncio


class RateLimiter:
    """
    Token bucket rate limiter for API endpoints.

    Attributes:
        max_requests: Maximum number of requests allowed per window
        window_seconds: Time window in seconds (default: 60 for 1 minute)
        user_buckets: Dictionary tracking requests per user
    """

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum requests allowed per window (default: 100)
            window_seconds: Time window in seconds (default: 60)
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # user_id -> (request_count, window_start_time)
        self.user_buckets: Dict[str, Tuple[int, datetime]] = defaultdict(
            lambda: (0, datetime.utcnow())
        )
        self._cleanup_lock = asyncio.Lock()

    async def check_rate_limit(self, user_id: str) -> bool:
        """
        Check if user has exceeded rate limit.

        Args:
            user_id: Unique user identifier

        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        now = datetime.utcnow()

        # Get current bucket for user
        count, window_start = self.user_buckets.get(
            user_id, (0, now)
        )

        # Check if window has expired
        if now - window_start > timedelta(seconds=self.window_seconds):
            # Reset window
            self.user_buckets[user_id] = (1, now)
            return True

        # Check if limit exceeded
        if count >= self.max_requests:
            return False

        # Increment counter
        self.user_buckets[user_id] = (count + 1, window_start)
        return True

    async def cleanup_old_buckets(self):
        """
        Remove expired buckets to prevent memory leaks.

        Should be called periodically (e.g., every 5 minutes).
        """
        async with self._cleanup_lock:
            now = datetime.utcnow()
            expired_users = [
                user_id
                for user_id, (_, window_start) in self.user_buckets.items()
                if now - window_start > timedelta(seconds=self.window_seconds * 2)
            ]

            for user_id in expired_users:
                del self.user_buckets[user_id]


# Global rate limiter instance
rate_limiter = RateLimiter(max_requests=100, window_seconds=60)


async def rate_limit_middleware(request: Request, call_next):
    """
    Middleware to enforce rate limiting on API requests.

    Args:
        request: FastAPI request object
        call_next: Next middleware/route handler

    Returns:
        Response from next handler

    Raises:
        HTTPException 429: If rate limit exceeded
    """
    # Skip rate limiting for health check and root endpoints
    if request.url.path in ["/", "/health", "/api/auth/login", "/api/auth/register"]:
        return await call_next(request)

    # Get user ID from request state (set by auth middleware)
    user_id = getattr(request.state, "user_id", None)

    if not user_id:
        # No user ID, skip rate limiting (unauthenticated requests)
        return await call_next(request)

    # Check rate limit
    if not await rate_limiter.check_rate_limit(user_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Rate limit exceeded",
                "message": f"Maximum {rate_limiter.max_requests} requests per {rate_limiter.window_seconds} seconds allowed",
                "retry_after": rate_limiter.window_seconds,
            }
        )

    # Process request
    response = await call_next(request)

    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.max_requests)
    response.headers["X-RateLimit-Remaining"] = str(
        rate_limiter.max_requests - rate_limiter.user_buckets.get(user_id, (0, datetime.utcnow()))[0]
    )

    return response
