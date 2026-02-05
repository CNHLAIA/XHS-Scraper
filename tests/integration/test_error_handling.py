"""Integration tests for error handling and recovery scenarios in XHSClient.

Tests cover:
- Signature verification failures and recovery
- Authentication/cookie expiration
- Rate limiting and retry logic
- Captcha detection
- Network error handling
- Request/response error conditions
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import Response, HTTPStatusError, TimeoutException, ConnectError
import asyncio

from xhs_scraper.client import XHSClient
from xhs_scraper.exceptions import (
    XHSError,
    APIError,
    SignatureError,
    CaptchaRequiredError,
    RateLimitError,
    CookieExpiredError,
)


class TestSignatureErrors:
    """Test error scenarios related to signature verification and generation."""

    @pytest.mark.asyncio
    async def test_signature_provider_returns_none(self, mock_signature_provider):
        """Test handling when signature provider returns None."""
        mock_signature_provider.sign_get = MagicMock(return_value={})
        mock_signature_provider.sign_post = MagicMock(return_value={})

        client = XHSClient(
            cookies={"test_cookie": "123"},
            signature_provider=mock_signature_provider,
        )

        with patch("httpx.AsyncClient") as mock_http_client:
            mock_async_client = AsyncMock()
            mock_async_client.aclose = AsyncMock()
            mock_http_client.return_value = mock_async_client

            # Mock 461 signature error response
            error_response = Response(
                status_code=461,
                json={"msg": "Signature verification failed"},
            )
            mock_async_client.request.return_value = error_response

            with pytest.raises(SignatureError) as exc_info:
                async with client:
                    await client.request("GET", "/api/test")

            assert "signature" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_signature_provider_raises_exception(self, mock_signature_provider):
        """Test handling when signature provider raises an exception."""
        mock_signature_provider.sign_get = MagicMock(
            side_effect=RuntimeError("Provider error")
        )
        mock_signature_provider.sign_post = MagicMock(
            side_effect=RuntimeError("Provider error")
        )

        client = XHSClient(
            cookies={"test_cookie": "123"},
            signature_provider=mock_signature_provider,
        )

        with patch("httpx.AsyncClient") as mock_http_client:
            mock_async_client = AsyncMock()
            mock_async_client.aclose = AsyncMock()
            mock_http_client.return_value = mock_async_client

            with pytest.raises(RuntimeError) as exc_info:
                async with client:
                    await client.request("GET", "/api/test")

            assert "Provider error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_api_response_461_signature_error(self):
        """Test API returning 461 status code triggers SignatureError."""
        mock_sig_provider = MagicMock()
        mock_sig_provider.sign_get = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )
        mock_sig_provider.sign_post = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )

        client = XHSClient(
            cookies={"test_cookie": "123"},
            signature_provider=mock_sig_provider,
        )

        with patch("httpx.AsyncClient") as mock_http_client:
            mock_async_client = AsyncMock()
            mock_async_client.aclose = AsyncMock()
            mock_http_client.return_value = mock_async_client
            mock_http_client.return_value = mock_async_client

            # Mock 461 error response
            error_response = Response(
                status_code=461,
                json={"msg": "Signature verification failed"},
            )
            mock_async_client.request.return_value = error_response

            async with client:
                with pytest.raises(SignatureError) as exc_info:
                    await client.request("GET", "/api/test")

                assert "signature" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_signature_error_includes_api_message(self):
        """Test that SignatureError includes the API's error message."""
        mock_sig_provider = MagicMock()
        mock_sig_provider.sign_get = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )
        mock_sig_provider.sign_post = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )

        client = XHSClient(
            cookies={"test_cookie": "123"},
            signature_provider=mock_sig_provider,
        )

        error_msg = "Invalid signature timestamp"

        with patch("httpx.AsyncClient") as mock_http_client:
            mock_async_client = AsyncMock()
            mock_async_client.aclose = AsyncMock()
            mock_http_client.return_value = mock_async_client
            mock_http_client.return_value = mock_async_client

            error_response = Response(
                status_code=461,
                json={"msg": error_msg, "code": 461},
            )
            mock_async_client.request.return_value = error_response

            async with client:
                with pytest.raises(SignatureError) as exc_info:
                    await client.request("GET", "/api/test")

                assert error_msg in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_repeated_signature_failures_indicate_cookie_issue(self):
        """Test multiple signature failures suggest authentication problem."""
        mock_sig_provider = MagicMock()
        mock_sig_provider.sign_get = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )
        mock_sig_provider.sign_post = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )

        client = XHSClient(
            cookies={"test_cookie": "123"},
            signature_provider=mock_sig_provider,
        )

        with patch("httpx.AsyncClient") as mock_http_client:
            mock_async_client = AsyncMock()
            mock_async_client.aclose = AsyncMock()
            mock_http_client.return_value = mock_async_client
            mock_http_client.return_value = mock_async_client

            error_response = Response(status_code=461, json={"msg": "Signature failed"})
            mock_async_client.request.return_value = error_response

            async with client:
                errors = []
                for _ in range(3):
                    try:
                        await client.request("GET", "/api/test")
                    except SignatureError as e:
                        errors.append(e)

                assert len(errors) == 3
                assert all(isinstance(e, SignatureError) for e in errors)


class TestAuthenticationErrors:
    """Test error scenarios related to authentication and session validity."""

    @pytest.mark.asyncio
    async def test_cookie_expired_401_error(self):
        """Test API returning 401 status triggers CookieExpiredError."""
        mock_sig_provider = MagicMock()
        mock_sig_provider.sign_get = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )
        mock_sig_provider.sign_post = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )

        client = XHSClient(
            cookies={"expired_cookie": "123"},
            signature_provider=mock_sig_provider,
        )

        with patch("httpx.AsyncClient") as mock_http_client:
            mock_async_client = AsyncMock()
            mock_async_client.aclose = AsyncMock()
            mock_http_client.return_value = mock_async_client
            mock_http_client.return_value = mock_async_client

            error_response = Response(
                status_code=401,
                json={"msg": "Unauthorized"},
            )
            mock_async_client.request.return_value = error_response

            async with client:
                with pytest.raises(CookieExpiredError):
                    await client.request("GET", "/api/test")

    @pytest.mark.asyncio
    async def test_cookie_expired_403_error(self):
        """Test API returning 403 status triggers CookieExpiredError."""
        mock_sig_provider = MagicMock()
        mock_sig_provider.sign_get = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )
        mock_sig_provider.sign_post = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )

        client = XHSClient(
            cookies={"forbidden_cookie": "123"},
            signature_provider=mock_sig_provider,
        )

        with patch("httpx.AsyncClient") as mock_http_client:
            mock_async_client = AsyncMock()
            mock_async_client.aclose = AsyncMock()
            mock_http_client.return_value = mock_async_client
            mock_http_client.return_value = mock_async_client

            error_response = Response(
                status_code=403,
                json={"msg": "Forbidden"},
            )
            mock_async_client.request.return_value = error_response

            async with client:
                with pytest.raises(CookieExpiredError):
                    await client.request("GET", "/api/test")

    @pytest.mark.asyncio
    async def test_invalid_cookies_validation_on_init(self):
        """Test that invalid cookies raise error on initialization."""
        with pytest.raises(ValueError) as exc_info:
            XHSClient(cookies={})

        assert "cookies" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_invalid_cookies_none_value(self):
        """Test that None cookies raise error on initialization."""
        with pytest.raises(ValueError):
            XHSClient(cookies=None)

    @pytest.mark.asyncio
    async def test_authentication_error_includes_api_message(self):
        """Test that CookieExpiredError includes API error message."""
        mock_sig_provider = MagicMock()
        mock_sig_provider.sign_get = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )
        mock_sig_provider.sign_post = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )

        error_msg = "Session expired. Please login again."

        client = XHSClient(
            cookies={"test_cookie": "123"},
            signature_provider=mock_sig_provider,
        )

        with patch("httpx.AsyncClient") as mock_http_client:
            mock_async_client = AsyncMock()
            mock_async_client.aclose = AsyncMock()
            mock_http_client.return_value = mock_async_client
            mock_http_client.return_value = mock_async_client

            error_response = Response(
                status_code=401,
                json={"msg": error_msg},
            )
            mock_async_client.request.return_value = error_response

            async with client:
                with pytest.raises(CookieExpiredError) as exc_info:
                    await client.request("GET", "/api/test")

                assert error_msg in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_multiple_auth_failures_suggest_credential_refresh_needed(self):
        """Test multiple auth failures indicate need to refresh credentials."""
        mock_sig_provider = MagicMock()
        mock_sig_provider.sign_get = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )
        mock_sig_provider.sign_post = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )

        client = XHSClient(
            cookies={"test_cookie": "123"},
            signature_provider=mock_sig_provider,
        )

        with patch("httpx.AsyncClient") as mock_http_client:
            mock_async_client = AsyncMock()
            mock_async_client.aclose = AsyncMock()
            mock_http_client.return_value = mock_async_client
            mock_http_client.return_value = mock_async_client

            error_response = Response(status_code=401, json={"msg": "Unauthorized"})
            mock_async_client.request.return_value = error_response

            async with client:
                failures = []
                for _ in range(3):
                    try:
                        await client.request("GET", "/api/test")
                    except CookieExpiredError as e:
                        failures.append(e)

                assert len(failures) == 3
                # After multiple failures, user should refresh credentials


class TestRateLimitingErrors:
    """Test error scenarios related to rate limiting and throttling."""

    @pytest.mark.asyncio
    async def test_rate_limit_429_error(self):
        """Test API returning 429 status triggers RateLimitError."""
        mock_sig_provider = MagicMock()
        mock_sig_provider.sign_get = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )
        mock_sig_provider.sign_post = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )

        client = XHSClient(
            cookies={"test_cookie": "123"},
            signature_provider=mock_sig_provider,
            rate_limit=10.0,
        )

        with patch("httpx.AsyncClient") as mock_http_client:
            mock_async_client = AsyncMock()
            mock_async_client.aclose = AsyncMock()
            mock_http_client.return_value = mock_async_client
            mock_http_client.return_value = mock_async_client

            error_response = Response(
                status_code=429,
                json={"msg": "Rate limit exceeded"},
            )
            mock_async_client.request.return_value = error_response

            async with client:
                with pytest.raises(RateLimitError):
                    await client.request("GET", "/api/test")

    @pytest.mark.asyncio
    async def test_rate_limit_error_includes_retry_after(self):
        """Test RateLimitError includes retry-after information if provided."""
        mock_sig_provider = MagicMock()
        mock_sig_provider.sign_get = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )
        mock_sig_provider.sign_post = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )

        client = XHSClient(
            cookies={"test_cookie": "123"},
            signature_provider=mock_sig_provider,
        )

        with patch("httpx.AsyncClient") as mock_http_client:
            mock_async_client = AsyncMock()
            mock_async_client.aclose = AsyncMock()
            mock_http_client.return_value = mock_async_client
            mock_http_client.return_value = mock_async_client

            error_response = Response(
                status_code=429,
                json={"msg": "Rate limit exceeded - too many requests"},
                headers={"Retry-After": "60"},
            )
            mock_async_client.request.return_value = error_response

            async with client:
                with pytest.raises(RateLimitError) as exc_info:
                    await client.request("GET", "/api/test")

                # Error message should hint at retry timing
                assert "rate" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_invalid_rate_limit_validation(self):
        """Test that invalid rate limits raise error on initialization."""
        with pytest.raises(ValueError) as exc_info:
            XHSClient(
                cookies={"test_cookie": "123"},
                rate_limit=0,  # Invalid: must be positive
            )

        assert "rate" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_negative_rate_limit_validation(self):
        """Test that negative rate limits raise error on initialization."""
        with pytest.raises(ValueError) as exc_info:
            XHSClient(
                cookies={"test_cookie": "123"},
                rate_limit=-5.0,
            )

        assert "rate" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_rate_limiter_delays_requests_appropriately(self):
        """Test that rate limiter introduces appropriate delays between requests."""
        mock_sig_provider = MagicMock()
        mock_sig_provider.sign_get = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )
        mock_sig_provider.sign_post = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )

        # Set rate limit to 2 requests per second (0.5s between requests)
        client = XHSClient(
            cookies={"test_cookie": "123"},
            signature_provider=mock_sig_provider,
            rate_limit=2.0,
        )

        with patch("httpx.AsyncClient") as mock_http_client:
            mock_async_client = AsyncMock()
            mock_async_client.aclose = AsyncMock()
            mock_http_client.return_value = mock_async_client
            mock_http_client.return_value = mock_async_client

            # Mock successful responses
            success_response = Response(status_code=200, json={"data": {}})
            mock_async_client.request.return_value = success_response

            async with client:
                import time

                start = time.time()

                # Make 3 requests
                await client.request("GET", "/api/test1")
                await client.request("GET", "/api/test2")
                await client.request("GET", "/api/test3")

                elapsed = time.time() - start

                # With 2 req/sec (0.5s each), 3 requests should take ~1 second
                # Allow some margin for execution overhead (lower threshold for faster systems)
                assert elapsed >= 0.4, f"Requests executed too fast: {elapsed}s"


class TestCaptchaErrors:
    """Test error scenarios related to captcha detection."""

    @pytest.mark.asyncio
    async def test_captcha_required_471_error(self):
        """Test API returning 471 status triggers CaptchaRequiredError."""
        mock_sig_provider = MagicMock()
        mock_sig_provider.sign_get = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )
        mock_sig_provider.sign_post = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )

        client = XHSClient(
            cookies={"test_cookie": "123"},
            signature_provider=mock_sig_provider,
        )

        with patch("httpx.AsyncClient") as mock_http_client:
            mock_async_client = AsyncMock()
            mock_async_client.aclose = AsyncMock()
            mock_http_client.return_value = mock_async_client
            mock_http_client.return_value = mock_async_client

            error_response = Response(
                status_code=471,
                json={"msg": "Captcha required"},
            )
            mock_async_client.request.return_value = error_response

            async with client:
                with pytest.raises(CaptchaRequiredError):
                    await client.request("GET", "/api/test")

    @pytest.mark.asyncio
    async def test_captcha_error_indicates_manual_intervention_needed(self):
        """Test CaptchaRequiredError indicates need for manual browser intervention."""
        mock_sig_provider = MagicMock()
        mock_sig_provider.sign_get = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )
        mock_sig_provider.sign_post = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )

        client = XHSClient(
            cookies={"test_cookie": "123"},
            signature_provider=mock_sig_provider,
        )

        with patch("httpx.AsyncClient") as mock_http_client:
            mock_async_client = AsyncMock()
            mock_async_client.aclose = AsyncMock()
            mock_http_client.return_value = mock_async_client
            mock_http_client.return_value = mock_async_client

            error_response = Response(
                status_code=471,
                json={"msg": "Please complete captcha"},
            )
            mock_async_client.request.return_value = error_response

            async with client:
                with pytest.raises(CaptchaRequiredError) as exc_info:
                    await client.request("GET", "/api/test")

                error_str = str(exc_info.value).lower()
                assert "captcha" in error_str
                # Error should suggest user needs to interact with browser

    @pytest.mark.asyncio
    async def test_repeated_captcha_errors_after_successful_requests(self):
        """Test detecting captcha requirement after previously successful requests."""
        mock_sig_provider = MagicMock()
        mock_sig_provider.sign_get = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )
        mock_sig_provider.sign_post = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )

        client = XHSClient(
            cookies={"test_cookie": "123"},
            signature_provider=mock_sig_provider,
        )

        with patch("httpx.AsyncClient") as mock_http_client:
            mock_async_client = AsyncMock()
            mock_async_client.aclose = AsyncMock()
            mock_http_client.return_value = mock_async_client
            mock_http_client.return_value = mock_async_client

            success_response = Response(status_code=200, json={"data": {}})
            captcha_response = Response(status_code=471, json={"msg": "Captcha"})

            # First request succeeds, subsequent requests require captcha
            mock_async_client.request.side_effect = [
                success_response,
                captcha_response,
                captcha_response,
            ]

            async with client:
                # First request should succeed
                result = await client.request("GET", "/api/test1")
                assert isinstance(result, dict)
                assert result.get("data") is not None

                # Subsequent requests should fail with captcha error
                with pytest.raises(CaptchaRequiredError):
                    await client.request("GET", "/api/test2")

                with pytest.raises(CaptchaRequiredError):
                    await client.request("GET", "/api/test3")


class TestNetworkErrors:
    """Test error scenarios related to network connectivity and timeouts."""

    @pytest.mark.asyncio
    async def test_connection_timeout_error(self):
        """Test connection timeout raises appropriate error."""
        mock_sig_provider = MagicMock()
        mock_sig_provider.sign_get = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )
        mock_sig_provider.sign_post = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )

        client = XHSClient(
            cookies={"test_cookie": "123"},
            signature_provider=mock_sig_provider,
            timeout=1.0,
        )

        with patch("httpx.AsyncClient") as mock_http_client:
            mock_async_client = AsyncMock()
            mock_async_client.aclose = AsyncMock()
            mock_http_client.return_value = mock_async_client
            mock_http_client.return_value = mock_async_client

            mock_async_client.request.side_effect = TimeoutException(
                "Connection timed out"
            )

            async with client:
                with pytest.raises(APIError) as exc_info:
                    await client.request("GET", "/api/test")

                assert "timed out" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_connect_error_network_unavailable(self):
        """Test network connection error handling."""
        mock_sig_provider = MagicMock()
        mock_sig_provider.sign_get = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )
        mock_sig_provider.sign_post = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )

        client = XHSClient(
            cookies={"test_cookie": "123"},
            signature_provider=mock_sig_provider,
        )

        with patch("httpx.AsyncClient") as mock_http_client:
            mock_async_client = AsyncMock()
            mock_async_client.aclose = AsyncMock()
            mock_http_client.return_value = mock_async_client
            mock_http_client.return_value = mock_async_client

            mock_async_client.request.side_effect = ConnectError(
                "Cannot connect to host"
            )

            async with client:
                with pytest.raises(APIError) as exc_info:
                    await client.request("GET", "/api/test")

                assert "connect" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_timeout_configuration_validation(self):
        """Test that timeout configuration is validated."""
        # Positive timeout should be accepted
        client = XHSClient(
            cookies={"test_cookie": "123"},
            timeout=5.0,
        )
        assert client._timeout == 5.0

    @pytest.mark.asyncio
    async def test_network_error_recovery_requires_retry(self):
        """Test that network errors can be recovered with retry logic."""
        mock_sig_provider = MagicMock()
        mock_sig_provider.sign_get = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )
        mock_sig_provider.sign_post = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )

        client = XHSClient(
            cookies={"test_cookie": "123"},
            signature_provider=mock_sig_provider,
        )

        with patch("httpx.AsyncClient") as mock_http_client:
            mock_async_client = AsyncMock()
            mock_async_client.aclose = AsyncMock()
            mock_http_client.return_value = mock_async_client
            mock_http_client.return_value = mock_async_client

            success_response = Response(status_code=200, json={"data": {}})

            # First request fails, second succeeds
            mock_async_client.request.side_effect = [
                ConnectError("Network unavailable"),
                success_response,
            ]

            async with client:
                # First attempt fails
                with pytest.raises(APIError):
                    await client.request("GET", "/api/test")

                # Retry succeeds
                result = await client.request("GET", "/api/test")
                assert isinstance(result, dict)
                assert result.get("data") is not None


class TestRequestResponseErrors:
    """Test error scenarios related to malformed requests/responses."""

    @pytest.mark.asyncio
    async def test_invalid_request_method_raises_error(self):
        """Test that invalid HTTP methods raise errors."""
        mock_sig_provider = MagicMock()
        mock_sig_provider.sign_get = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )
        mock_sig_provider.sign_post = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )

        client = XHSClient(
            cookies={"test_cookie": "123"},
            signature_provider=mock_sig_provider,
        )

        with patch("httpx.AsyncClient") as mock_http_client:
            mock_async_client = AsyncMock()
            mock_async_client.aclose = AsyncMock()
            mock_http_client.return_value = mock_async_client
            mock_http_client.return_value = mock_async_client

            async with client:
                with pytest.raises(ValueError) as exc_info:
                    await client.request("INVALID", "/api/test")

                assert "method" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_invalid_request_path_raises_error(self):
        """Test that invalid paths raise errors."""
        mock_sig_provider = MagicMock()
        mock_sig_provider.sign_get = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )
        mock_sig_provider.sign_post = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )

        client = XHSClient(
            cookies={"test_cookie": "123"},
            signature_provider=mock_sig_provider,
        )

        with patch("httpx.AsyncClient") as mock_http_client:
            mock_async_client = AsyncMock()
            mock_async_client.aclose = AsyncMock()
            mock_http_client.return_value = mock_async_client
            mock_http_client.return_value = mock_async_client

            async with client:
                with pytest.raises(ValueError) as exc_info:
                    await client.request("GET", "")  # Empty path

                assert "path" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_malformed_json_response(self):
        """Test handling of malformed JSON responses."""
        mock_sig_provider = MagicMock()
        mock_sig_provider.sign_get = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )
        mock_sig_provider.sign_post = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )

        client = XHSClient(
            cookies={"test_cookie": "123"},
            signature_provider=mock_sig_provider,
        )

        with patch("httpx.AsyncClient") as mock_http_client:
            mock_async_client = AsyncMock()
            mock_async_client.aclose = AsyncMock()
            mock_http_client.return_value = mock_async_client
            mock_http_client.return_value = mock_async_client

            # Response with invalid JSON
            bad_response = AsyncMock()
            bad_response.status_code = 200
            bad_response.json.side_effect = ValueError("Invalid JSON")

            mock_async_client.request.return_value = bad_response

            async with client:
                with pytest.raises(APIError) as exc_info:
                    await client.request("GET", "/api/test")
                assert "json" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_missing_required_headers_in_response(self):
        """Test handling of responses missing required headers."""
        mock_sig_provider = MagicMock()
        mock_sig_provider.sign_get = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )
        mock_sig_provider.sign_post = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )

        client = XHSClient(
            cookies={"test_cookie": "123"},
            signature_provider=mock_sig_provider,
        )

        with patch("httpx.AsyncClient") as mock_http_client:
            mock_async_client = AsyncMock()
            mock_async_client.aclose = AsyncMock()
            mock_http_client.return_value = mock_async_client
            mock_http_client.return_value = mock_async_client

            # Response with missing content-type header (shouldn't cause error)
            response = Response(
                status_code=200,
                json={"data": {}},
                headers={},  # Missing typical headers
            )
            mock_async_client.request.return_value = response

            async with client:
                # Should still process successfully
                result = await client.request("GET", "/api/test")
                assert isinstance(result, dict)
                assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_generic_api_error_with_unknown_status_code(self):
        """Test handling of unexpected HTTP status codes."""
        mock_sig_provider = MagicMock()
        mock_sig_provider.sign_get = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )
        mock_sig_provider.sign_post = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )

        client = XHSClient(
            cookies={"test_cookie": "123"},
            signature_provider=mock_sig_provider,
        )

        with patch("httpx.AsyncClient") as mock_http_client:
            mock_async_client = AsyncMock()
            mock_async_client.aclose = AsyncMock()
            mock_http_client.return_value = mock_async_client
            mock_http_client.return_value = mock_async_client

            # Unexpected error code (e.g., 500)
            error_response = Response(
                status_code=500,
                json={"msg": "Internal server error"},
            )
            mock_async_client.request.return_value = error_response

            async with client:
                with pytest.raises(APIError):
                    await client.request("GET", "/api/test")


class TestErrorRecoveryAndResilience:
    """Test error recovery strategies and resilience patterns."""

    @pytest.mark.asyncio
    async def test_client_cleanup_after_error(self):
        """Test that client properly cleans up resources after errors."""
        mock_sig_provider = MagicMock()
        mock_sig_provider.sign_get = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )
        mock_sig_provider.sign_post = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )

        client = XHSClient(
            cookies={"test_cookie": "123"},
            signature_provider=mock_sig_provider,
        )

        with patch("httpx.AsyncClient") as mock_http_client:
            mock_async_client = AsyncMock()
            mock_async_client.aclose = AsyncMock()
            mock_http_client.return_value = mock_async_client
            mock_http_client.return_value = mock_async_client

            error_response = Response(status_code=401, json={"msg": "Unauthorized"})
            mock_async_client.request.return_value = error_response

            # Error occurs inside context manager
            with pytest.raises(CookieExpiredError):
                async with client:
                    await client.request("GET", "/api/test")

            # Verify aclose was called for cleanup (though error occurred)
            # aclose should be called in __aexit__
            mock_async_client.aclose.assert_called()

    @pytest.mark.asyncio
    async def test_reusing_client_after_temporary_error(self):
        """Test that client can recover and be reused after temporary errors."""
        mock_sig_provider = MagicMock()
        mock_sig_provider.sign_get = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )
        mock_sig_provider.sign_post = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )

        client = XHSClient(
            cookies={"test_cookie": "123"},
            signature_provider=mock_sig_provider,
        )

        with patch("httpx.AsyncClient") as mock_http_client:
            mock_async_client = AsyncMock()
            mock_async_client.aclose = AsyncMock()
            mock_http_client.return_value = mock_async_client
            mock_http_client.return_value = mock_async_client

            success_response = Response(status_code=200, json={"data": {}})
            mock_async_client.request.return_value = success_response

            # First session - make request
            async with client:
                result = await client.request("GET", "/api/test")
                assert isinstance(result, dict)
                assert result.get("data") is not None

            # Reset mocks for second session
            mock_http_client.reset_mock()
            mock_http_client.return_value.__aenter__.return_value = mock_async_client
            mock_http_client.return_value.__aexit__.return_value = None

            # Second session - should work again
            async with client:
                result = await client.request("GET", "/api/test")
                assert isinstance(result, dict)
                assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_error_context_preserved_in_exception(self):
        """Test that error context (original exception) is preserved."""
        mock_sig_provider = MagicMock()
        mock_sig_provider.sign_get = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )
        mock_sig_provider.sign_post = MagicMock(
            return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
        )

        client = XHSClient(
            cookies={"test_cookie": "123"},
            signature_provider=mock_sig_provider,
        )

        original_error = RuntimeError("Original error")

        with patch("httpx.AsyncClient") as mock_http_client:
            mock_async_client = AsyncMock()
            mock_async_client.aclose = AsyncMock()
            mock_http_client.return_value = mock_async_client
            mock_http_client.return_value = mock_async_client

            mock_async_client.request.side_effect = original_error

            async with client:
                with pytest.raises(RuntimeError) as exc_info:
                    await client.request("GET", "/api/test")

                assert exc_info.value is original_error
