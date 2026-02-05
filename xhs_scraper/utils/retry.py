"""Retry utilities for XHS scraper using tenacity."""

from functools import wraps
from typing import Any, Callable, Optional, Type, TypeVar

from tenacity import (
    Attempt,
    BaseRetrying,
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

# Exceptions to retry on
_RETRYABLE_EXCEPTIONS = (
    ConnectionError,
    TimeoutError,
    OSError,
)


def create_retry_decorator(
    max_retries: int = 5,
    initial_wait: float = 1.0,
    max_wait: float = 60.0,
    exception_types: Optional[tuple] = None,
) -> Callable:
    """Create a retry decorator with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        initial_wait: Initial wait time in seconds
        max_wait: Maximum wait time between retries
        exception_types: Tuple of exception types to retry on
                        (defaults to network errors)

    Returns:
        Retry decorator function
    """
    if exception_types is None:
        exception_types = _RETRYABLE_EXCEPTIONS

    # Build retry condition
    retry_condition = retry_if_exception_type(exception_types)

    # Apply retry decorator with exponential backoff
    def decorator(func: Callable) -> Callable:
        return retry(
            retry=retry_condition,
            stop=stop_after_attempt(max_retries),
            wait=wait_exponential(multiplier=initial_wait, max=max_wait),
            reraise=True,
        )(func)

    return decorator


def should_retry_http_error(status_code: int) -> bool:
    """Determine if HTTP error should be retried.

    Args:
        status_code: HTTP status code

    Returns:
        True if error should be retried, False otherwise

    Retry conditions:
        - 429: Rate limit (temporary)
        - 5xx: Server errors (temporary)

    Do not retry:
        - 461: Signature verification failed
        - 471: Captcha/security challenge
        - 4xx (except 429): Client errors (permanent)
    """
    # Retry server errors
    if 500 <= status_code < 600:
        return True

    # Retry specific 4xx errors
    if status_code == 429:  # Too Many Requests
        return True

    # Do not retry signature (461) or captcha (471) errors
    if status_code in (461, 471):
        return False

    # Do not retry other 4xx errors
    if 400 <= status_code < 500:
        return False

    return False
