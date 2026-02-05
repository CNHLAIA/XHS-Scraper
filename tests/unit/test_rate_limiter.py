"""Unit tests for xhs_scraper.utils.rate_limiter module."""

import pytest
import asyncio
import time
from xhs_scraper.utils.rate_limiter import TokenBucketRateLimiter


class TestTokenBucketRateLimiterInit:
    """Test TokenBucketRateLimiter initialization."""

    def test_init_with_valid_rate(self):
        """Initialize with valid rate."""
        limiter = TokenBucketRateLimiter(rate=10.0)
        assert limiter.rate == 10.0
        assert limiter.capacity == 10.0
        assert limiter.tokens == 10.0

    def test_init_with_custom_capacity(self):
        """Initialize with custom capacity."""
        limiter = TokenBucketRateLimiter(rate=5.0, capacity=20.0)
        assert limiter.rate == 5.0
        assert limiter.capacity == 20.0
        assert limiter.tokens == 20.0

    def test_init_with_zero_rate_raises_error(self):
        """Initialization with zero rate raises ValueError."""
        with pytest.raises(ValueError, match="Rate must be positive"):
            TokenBucketRateLimiter(rate=0)

    def test_init_with_negative_rate_raises_error(self):
        """Initialization with negative rate raises ValueError."""
        with pytest.raises(ValueError, match="Rate must be positive"):
            TokenBucketRateLimiter(rate=-5.0)

    def test_capacity_defaults_to_rate(self):
        """When capacity not specified, it defaults to rate."""
        limiter = TokenBucketRateLimiter(rate=7.5)
        assert limiter.capacity == 7.5


class TestTokenBucketRateLimiterAcquire:
    """Test TokenBucketRateLimiter.acquire() method."""

    @pytest.mark.asyncio
    async def test_acquire_single_token(self):
        """Acquire single token when available."""
        limiter = TokenBucketRateLimiter(rate=10.0)
        await limiter.acquire(1.0)
        assert limiter.tokens == 9.0

    @pytest.mark.asyncio
    async def test_acquire_multiple_tokens(self):
        """Acquire multiple tokens."""
        limiter = TokenBucketRateLimiter(rate=10.0)
        await limiter.acquire(3.0)
        assert limiter.tokens == 7.0

    @pytest.mark.asyncio
    async def test_acquire_all_tokens(self):
        """Acquire all available tokens."""
        limiter = TokenBucketRateLimiter(rate=5.0, capacity=5.0)
        await limiter.acquire(5.0)
        assert limiter.tokens == 0.0

    @pytest.mark.asyncio
    async def test_acquire_with_zero_tokens_raises_error(self):
        """Acquire zero tokens raises ValueError."""
        limiter = TokenBucketRateLimiter(rate=10.0)
        with pytest.raises(ValueError, match="Token request must be positive"):
            await limiter.acquire(0)

    @pytest.mark.asyncio
    async def test_acquire_with_negative_tokens_raises_error(self):
        """Acquire negative tokens raises ValueError."""
        limiter = TokenBucketRateLimiter(rate=10.0)
        with pytest.raises(ValueError, match="Token request must be positive"):
            await limiter.acquire(-1.0)

    @pytest.mark.asyncio
    async def test_acquire_blocks_until_tokens_available(self):
        """Acquire blocks when tokens unavailable, then waits."""
        limiter = TokenBucketRateLimiter(rate=10.0, capacity=1.0)

        start = time.monotonic()
        await limiter.acquire(1.0)
        await limiter.acquire(1.0)
        elapsed = time.monotonic() - start

        assert elapsed >= 0.09

    @pytest.mark.asyncio
    async def test_acquire_multiple_sequential_calls(self):
        """Multiple sequential acquire calls."""
        limiter = TokenBucketRateLimiter(rate=10.0)
        await limiter.acquire(2.0)
        assert limiter.tokens == 8.0
        await limiter.acquire(3.0)
        assert limiter.tokens == 5.0
        await limiter.acquire(5.0)
        assert limiter.tokens == 0.0

    @pytest.mark.asyncio
    async def test_acquire_timing_with_rate_refill(self):
        """Acquire waits appropriate time for rate refill."""
        limiter = TokenBucketRateLimiter(rate=2.0, capacity=1.0)

        await limiter.acquire(1.0)

        start = time.monotonic()
        await limiter.acquire(1.0)
        elapsed = time.monotonic() - start

        assert elapsed >= 0.4


class TestTokenBucketRateLimiterGetTokens:
    """Test TokenBucketRateLimiter.get_tokens() method."""

    def test_get_tokens_without_refill(self):
        """Get tokens immediately after creation."""
        limiter = TokenBucketRateLimiter(rate=10.0)
        assert limiter.get_tokens() == 10.0

    def test_get_tokens_after_refill(self):
        """Get tokens after time passes for refill."""
        limiter = TokenBucketRateLimiter(rate=5.0, capacity=10.0)
        limiter.tokens = 5.0
        limiter.last_update = time.monotonic() - 0.5

        tokens = limiter.get_tokens()
        assert tokens == 7.5

    def test_get_tokens_caps_at_capacity(self):
        """Get tokens never exceeds capacity."""
        limiter = TokenBucketRateLimiter(rate=10.0, capacity=10.0)
        limiter.last_update = time.monotonic() - 100

        tokens = limiter.get_tokens()
        assert tokens == 10.0

    def test_get_tokens_does_not_consume(self):
        """Get tokens does not modify internal state."""
        limiter = TokenBucketRateLimiter(rate=10.0)
        initial_tokens = limiter.tokens

        _ = limiter.get_tokens()
        assert limiter.tokens == initial_tokens

    def test_get_tokens_multiple_calls(self):
        """Multiple get_tokens calls return consistent values."""
        limiter = TokenBucketRateLimiter(rate=5.0)
        tokens1 = limiter.get_tokens()
        tokens2 = limiter.get_tokens()

        assert abs(tokens1 - tokens2) < 0.01


class TestTokenBucketRateLimiterConcurrency:
    """Test TokenBucketRateLimiter with concurrent operations."""

    @pytest.mark.asyncio
    async def test_concurrent_acquire_calls(self):
        """Multiple concurrent acquire calls."""
        limiter = TokenBucketRateLimiter(rate=100.0)

        await asyncio.gather(
            limiter.acquire(1.0),
            limiter.acquire(1.0),
            limiter.acquire(1.0),
        )

        assert limiter.tokens == 97.0

    @pytest.mark.asyncio
    async def test_many_concurrent_acquires(self):
        """Many concurrent acquire calls."""
        limiter = TokenBucketRateLimiter(rate=50.0)

        tasks = [limiter.acquire(0.5) for _ in range(10)]
        await asyncio.gather(*tasks)

        assert limiter.tokens == 45.0

    @pytest.mark.asyncio
    async def test_concurrent_acquire_and_get_tokens(self):
        """Concurrent acquire and get_tokens calls."""
        limiter = TokenBucketRateLimiter(rate=10.0)

        async def acquire_many():
            for _ in range(3):
                await limiter.acquire(0.5)

        await asyncio.gather(
            acquire_many(),
            asyncio.sleep(0.1),
        )

        tokens = limiter.get_tokens()
        assert tokens >= 0


class TestTokenBucketRateLimiterBehavior:
    """Test behavioral scenarios."""

    @pytest.mark.asyncio
    async def test_rate_limit_enforces_delay(self):
        """Rate limiter enforces minimum delay between requests."""
        limiter = TokenBucketRateLimiter(rate=2.0, capacity=1.0)

        start = time.monotonic()
        for _ in range(3):
            await limiter.acquire(1.0)
        elapsed = time.monotonic() - start

        assert elapsed >= 0.9

    @pytest.mark.asyncio
    async def test_burst_within_capacity(self):
        """Allow burst requests up to capacity."""
        limiter = TokenBucketRateLimiter(rate=2.0, capacity=5.0)

        start = time.monotonic()
        await asyncio.gather(
            limiter.acquire(1.0),
            limiter.acquire(1.0),
            limiter.acquire(1.0),
        )
        elapsed = time.monotonic() - start

        assert elapsed < 0.2

    @pytest.mark.asyncio
    async def test_fairness_across_tasks(self):
        """Rate limiter treats all tasks fairly."""
        limiter = TokenBucketRateLimiter(rate=10.0)
        timings = []

        async def acquire_and_record(task_id):
            start = time.monotonic()
            await limiter.acquire(1.0)
            timings.append((task_id, time.monotonic() - start))

        await asyncio.gather(
            acquire_and_record(1),
            acquire_and_record(2),
            acquire_and_record(3),
        )

        assert len(timings) == 3
