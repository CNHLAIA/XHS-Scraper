"""Unit tests for xhs_scraper.exceptions module."""

import pytest
from xhs_scraper.exceptions import (
    XHSError,
    CookieExpiredError,
    SignatureError,
    CaptchaRequiredError,
    RateLimitError,
    APIError,
)


class TestExceptionHierarchy:
    """Test exception class hierarchy."""

    def test_all_exceptions_inherit_from_xhs_error(self):
        """Verify all custom exceptions inherit from XHSError."""
        assert issubclass(CookieExpiredError, XHSError)
        assert issubclass(SignatureError, XHSError)
        assert issubclass(CaptchaRequiredError, XHSError)
        assert issubclass(RateLimitError, XHSError)
        assert issubclass(APIError, XHSError)

    def test_xhs_error_inherits_from_exception(self):
        """Verify XHSError is a proper exception."""
        assert issubclass(XHSError, Exception)


class TestXHSError:
    """Test base XHSError exception."""

    def test_xhs_error_can_be_raised(self):
        """Test raising XHSError."""
        with pytest.raises(XHSError):
            raise XHSError("Test error")

    def test_xhs_error_message(self):
        """Test XHSError message."""
        error = XHSError("Test message")
        assert str(error) == "Test message"


class TestCookieExpiredError:
    """Test CookieExpiredError exception."""

    def test_cookie_expired_error_can_be_raised(self):
        """Test raising CookieExpiredError."""
        with pytest.raises(CookieExpiredError):
            raise CookieExpiredError("Cookies expired")

    def test_cookie_expired_error_caught_by_xhs_error(self):
        """Test catching CookieExpiredError with XHSError."""
        with pytest.raises(XHSError):
            raise CookieExpiredError("Cookies expired")


class TestSignatureError:
    """Test SignatureError exception."""

    def test_signature_error_can_be_raised(self):
        """Test raising SignatureError."""
        with pytest.raises(SignatureError):
            raise SignatureError("Invalid signature")

    def test_signature_error_caught_by_xhs_error(self):
        """Test catching SignatureError with XHSError."""
        with pytest.raises(XHSError):
            raise SignatureError("Invalid signature")


class TestCaptchaRequiredError:
    """Test CaptchaRequiredError exception."""

    def test_captcha_required_error_can_be_raised(self):
        """Test raising CaptchaRequiredError."""
        with pytest.raises(CaptchaRequiredError):
            raise CaptchaRequiredError("Captcha required")

    def test_captcha_required_error_caught_by_xhs_error(self):
        """Test catching CaptchaRequiredError with XHSError."""
        with pytest.raises(XHSError):
            raise CaptchaRequiredError("Captcha required")


class TestRateLimitError:
    """Test RateLimitError exception."""

    def test_rate_limit_error_can_be_raised(self):
        """Test raising RateLimitError."""
        with pytest.raises(RateLimitError):
            raise RateLimitError("Rate limit exceeded")

    def test_rate_limit_error_caught_by_xhs_error(self):
        """Test catching RateLimitError with XHSError."""
        with pytest.raises(XHSError):
            raise RateLimitError("Rate limit exceeded")


class TestAPIError:
    """Test APIError exception with custom attributes."""

    def test_api_error_with_status_code_and_message(self):
        """Test APIError initialization with status code and message."""
        error = APIError(500, "Internal Server Error")
        assert error.status_code == 500
        assert error.message == "Internal Server Error"
        assert error.response_data is None

    def test_api_error_with_response_data(self):
        """Test APIError initialization with response data."""
        response_data = {"error": "Test", "code": 500}
        error = APIError(500, "Error occurred", response_data)
        assert error.status_code == 500
        assert error.message == "Error occurred"
        assert error.response_data == response_data

    def test_api_error_str_representation(self):
        """Test APIError string representation."""
        error = APIError(404, "Not Found")
        assert str(error) == "API Error 404: Not Found"

    def test_api_error_repr_representation(self):
        """Test APIError repr representation."""
        error = APIError(500, "Error", {"key": "value"})
        repr_str = repr(error)
        assert "APIError" in repr_str
        assert "status_code=500" in repr_str
        assert "message=" in repr_str

    def test_api_error_caught_by_xhs_error(self):
        """Test catching APIError with XHSError."""
        with pytest.raises(XHSError):
            raise APIError(503, "Service Unavailable")

    def test_api_error_specific_status_codes(self):
        """Test APIError with various HTTP status codes."""
        error_400 = APIError(400, "Bad Request")
        error_401 = APIError(401, "Unauthorized")
        error_403 = APIError(403, "Forbidden")
        error_500 = APIError(500, "Internal Server Error")

        assert error_400.status_code == 400
        assert error_401.status_code == 401
        assert error_403.status_code == 403
        assert error_500.status_code == 500
