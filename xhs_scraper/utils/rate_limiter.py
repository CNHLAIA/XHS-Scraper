"""Rate limiter utilities for XHS scraper."""

import asyncio
import time
from typing import Optional


class TokenBucketRateLimiter:
    """Token bucket rate limiter for async operations.

    Implements the token bucket algorithm to enforce rate limits.
    Allows bursts up to capacity while maintaining average rate.

    Args:
        rate: Requests per second (float)
        capacity: Maximum burst size (defaults to rate)
    """

    def __init__(self, rate: float, capacity: Optional[float] = None):
        """Initialize rate limiter.

        Args:
            rate: Requests per second
            capacity: Maximum tokens in bucket (defaults to rate)
        """
        if rate <= 0:
            raise ValueError("Rate must be positive")

        self.rate = rate
        self.capacity = capacity if capacity is not None else rate
        self.tokens = float(self.capacity)
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self, tokens: float = 1.0) -> None:
        """Acquire tokens, blocking until available.

        Args:
            tokens: Number of tokens to acquire (default: 1.0)

        Raises:
            ValueError: If tokens is negative or zero
        """
        if tokens <= 0:
            raise ValueError("Token request must be positive")

        while True:
            async with self._lock:
                now = time.monotonic()
                elapsed = now - self.last_update

                # Refill tokens based on elapsed time
                self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
                self.last_update = now

                # Check if tokens available
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return

            # Calculate wait time
            async with self._lock:
                tokens_needed = tokens - self.tokens
                wait_time = tokens_needed / self.rate

            await asyncio.sleep(wait_time)

    def get_tokens(self) -> float:
        """Get current token count without acquiring.

        Returns:
            Current number of tokens in bucket
        """
        now = time.monotonic()
        elapsed = now - self.last_update
        return min(self.capacity, self.tokens + elapsed * self.rate)
