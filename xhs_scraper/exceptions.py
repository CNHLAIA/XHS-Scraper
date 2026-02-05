"""
Custom exception classes for XHS scraper.

This module defines all exceptions used throughout the XHS scraper package.
Each exception class inherits from XHSError to enable unified error handling.
"""


class XHSError(Exception):
    """
    Base exception class for all XHS scraper errors.

    This is the parent exception for all custom exceptions in the xhs_scraper package.
    Use this to catch any XHS scraper-related error.
    """

    pass


class CookieExpiredError(XHSError):
    """
    Raised when authentication cookies are expired or invalid.

    This typically occurs when the session has timed out or credentials are no longer valid.
    The application should attempt to refresh or re-authenticate.
    """

    pass


class SignatureError(XHSError):
    """
    Raised when API request signature validation fails (HTTP 461).

    This error indicates that the X-s header signature is invalid or could not be generated.
    Common causes: request parameter tampering, timestamp mismatch, or incorrect signing algorithm.
    """

    pass


class CaptchaRequiredError(XHSError):
    """
    Raised when XHS requires CAPTCHA verification (HTTP 471).

    This error indicates anti-bot protection was triggered. The scraper should:
    - Implement exponential backoff before retrying
    - Consider rotating IP addresses or user agents
    - Evaluate if scraping intensity needs reduction
    """

    pass


class RateLimitError(XHSError):
    """
    Raised when API rate limit is exceeded (HTTP 429).

    This error indicates too many requests in a short time window.
    Implement exponential backoff and respect the rate limit quotas.
    """

    pass


class APIError(XHSError):
    """
    Raised for general API errors with detailed response information.

    This exception captures the HTTP status code, error message, and the full
    response data from the API for debugging and logging purposes.

    Attributes:
        status_code (int): HTTP status code from the response
        message (str): Error message describing what went wrong
        response_data (dict | None): Full API response data for inspection
    """

    def __init__(
        self, status_code: int, message: str, response_data: dict | None = None
    ):
        """
        Initialize APIError with status code and response details.

        Args:
            status_code (int): HTTP status code (e.g., 400, 500, 503)
            message (str): Human-readable error message
            response_data (dict | None): Optional full API response data
        """
        self.status_code = status_code
        self.message = message
        self.response_data = response_data
        super().__init__(f"API Error {status_code}: {message}")

    def __str__(self) -> str:
        """Return a formatted string representation of the error."""
        return f"API Error {self.status_code}: {self.message}"

    def __repr__(self) -> str:
        """Return a detailed representation of the error."""
        return (
            f"APIError(status_code={self.status_code}, "
            f"message={self.message!r}, "
            f"response_data={self.response_data!r})"
        )
