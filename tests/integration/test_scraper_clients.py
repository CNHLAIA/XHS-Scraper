"""Integration tests for XHSClient and scraper initialization.

Tests the core client functionality:
- Client initialization with various configurations
- Async context manager lifecycle
- Scraper attachment and access
- Rate limiter integration
- Signature provider integration
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import httpx

from xhs_scraper.client import XHSClient, _normalize_path
from xhs_scraper.exceptions import APIError
from xhs_scraper.signature import SignatureProvider
from xhs_scraper.utils.rate_limiter import TokenBucketRateLimiter


class TestNormalizePath:
    """Test path normalization utility."""

    def test_normalize_path_already_absolute(self):
        """Path starting with / should remain unchanged."""
        assert _normalize_path("/api/endpoint") == "/api/endpoint"

    def test_normalize_path_relative(self):
        """Path without / should be prefixed with /."""
        assert _normalize_path("api/endpoint") == "/api/endpoint"

    def test_normalize_path_empty_raises(self):
        """Empty path should raise ValueError."""
        with pytest.raises(ValueError, match="path must be non-empty"):
            _normalize_path("")

    def test_normalize_path_single_slash(self):
        """Single slash should remain unchanged."""
        assert _normalize_path("/") == "/"


class TestXHSClientInitialization:
    """Test XHSClient initialization."""

    def test_init_with_valid_cookies(self):
        """Client should initialize with valid cookies."""
        cookies = {"a": "b", "c": "d"}
        client = XHSClient(cookies=cookies)
        assert client.cookies == cookies

    def test_init_with_empty_cookies_raises(self):
        """Empty cookies should raise ValueError."""
        with pytest.raises(ValueError, match="cookies must be a non-empty mapping"):
            XHSClient(cookies={})

    def test_init_with_non_mapping_cookies_raises(self):
        """Non-mapping cookies should raise ValueError."""
        with pytest.raises(ValueError, match="cookies must be a non-empty mapping"):
            XHSClient(cookies="invalid")

    def test_init_with_rate_limit_zero_raises(self):
        """Rate limit of 0 should raise ValueError."""
        with pytest.raises(ValueError, match="rate_limit must be positive"):
            XHSClient(cookies={"a1": "test_a1_value"}, rate_limit=0)

    def test_init_with_rate_limit_negative_raises(self):
        """Negative rate limit should raise ValueError."""
        with pytest.raises(ValueError, match="rate_limit must be positive"):
            XHSClient(cookies={"a1": "test_a1_value"}, rate_limit=-1)

    def test_init_with_valid_rate_limit(self):
        """Client should initialize with valid rate limit."""
        client = XHSClient(cookies={"a1": "test_a1_value"}, rate_limit=10.0)
        assert client._rate_limiter is not None
        assert isinstance(client._rate_limiter, TokenBucketRateLimiter)

    def test_init_without_rate_limit(self):
        """Client should initialize without rate limiter when not specified."""
        client = XHSClient(cookies={"a1": "test_a1_value"})
        assert client._rate_limiter is None

    def test_init_with_custom_timeout(self):
        """Client should accept custom timeout."""
        client = XHSClient(cookies={"a1": "test_a1_value"}, timeout=60.0)
        assert client._timeout == 60.0

    def test_init_with_default_timeout(self):
        """Client should use default timeout if not specified."""
        client = XHSClient(cookies={"a1": "test_a1_value"})
        assert client._timeout == 30.0

    def test_init_with_custom_signature_provider(self):
        """Client should accept custom signature provider."""
        mock_provider = Mock(spec=SignatureProvider)
        client = XHSClient(
            cookies={"a1": "test_a1_value"}, signature_provider=mock_provider
        )
        assert client._signature_provider is mock_provider

    def test_init_with_default_signature_provider(self):
        """Client should use XHShowSignatureProvider by default."""
        with patch("xhs_scraper.client.XHShowSignatureProvider"):
            client = XHSClient(cookies={"a1": "test_a1_value"})
            assert client._signature_provider is not None


class TestXHSClientContextManager:
    """Test XHSClient async context manager lifecycle."""

    @pytest.mark.asyncio
    async def test_context_manager_enters(self):
        """Client should enter context and create httpx client."""
        client = XHSClient(cookies={"a1": "test_a1_value"})
        assert client._http is None

        async with client as ctx:
            assert ctx is client
            assert client._http is not None
            assert isinstance(client._http, httpx.AsyncClient)

    @pytest.mark.asyncio
    async def test_context_manager_exits(self):
        """Client should cleanup on exit."""
        client = XHSClient(cookies={"a1": "test_a1_value"})
        async with client:
            assert client._http is not None

        assert client._http is None

    @pytest.mark.asyncio
    async def test_aclose_without_context(self):
        """aclose() should be safe when called directly."""
        client = XHSClient(cookies={"a1": "test_a1_value"})
        assert client._http is None
        await client.aclose()
        assert client._http is None

    @pytest.mark.asyncio
    async def test_aclose_with_client(self):
        """aclose() should close the httpx client."""
        client = XHSClient(cookies={"a1": "test_a1_value"})
        async with client:
            assert client._http is not None
            await client.aclose()
            assert client._http is None


class TestXHSClientScraperAttachment:
    """Test scraper attachment to client."""

    def test_scrapers_attached_on_init(self):
        """Client should attach scraper objects on initialization."""
        client = XHSClient(cookies={"a1": "test_a1_value"})
        assert client._scrapers is not None
        assert client._scrapers.notes is not None
        assert client._scrapers.users is not None
        assert client._scrapers.comments is not None
        assert client._scrapers.search is not None

    def test_scraper_properties_accessible(self):
        """Scraper objects should be accessible via properties."""
        client = XHSClient(cookies={"a1": "test_a1_value"})
        assert client.notes is not None
        assert client.users is not None
        assert client.comments is not None
        assert client.search is not None

    def test_scraper_properties_return_same_objects(self):
        """Scraper properties should return the same objects."""
        client = XHSClient(cookies={"a1": "test_a1_value"})
        assert client.notes is client.notes
        assert client.users is client.users
        assert client.comments is client.comments
        assert client.search is client.search

    def test_scrapers_have_client_reference(self):
        """Scraper objects should have reference to client."""
        client = XHSClient(cookies={"a1": "test_a1_value"})
        assert client.notes._client is client
        assert client.users._client is client
        assert client.comments._client is client
        assert client.search._client is client


class TestXHSClientRequest:
    """Test XHSClient._request method."""

    @pytest.mark.asyncio
    async def test_request_without_context_raises(self):
        """Request outside context should raise RuntimeError."""
        client = XHSClient(cookies={"a1": "test_a1_value"})
        with pytest.raises(
            RuntimeError, match="must be used as an async context manager"
        ):
            await client._request("GET", "/api/test")

    @pytest.mark.asyncio
    async def test_request_invalid_method_raises(self):
        """Invalid HTTP method should raise ValueError."""
        client = XHSClient(cookies={"a1": "test_a1_value"})
        async with client:
            with pytest.raises(ValueError, match="method must be GET or POST"):
                await client._request("PUT", "/api/test")

    @pytest.mark.asyncio
    async def test_request_empty_path_raises(self):
        """Empty path should raise ValueError."""
        client = XHSClient(cookies={"a1": "test_a1_value"})
        async with client:
            with pytest.raises(ValueError, match="path must be non-empty"):
                await client._request("GET", "")

    @pytest.mark.asyncio
    async def test_request_normalizes_path(self):
        """Request should normalize path to absolute."""
        client = XHSClient(cookies={"a1": "test_a1_value"})
        async with client:
            with patch.object(
                client._http, "request", new_callable=AsyncMock
            ) as mock_req:
                mock_req.return_value = AsyncMock(
                    status_code=200, json=MagicMock(return_value={"success": True})
                )

                await client._request("GET", "api/test")

                # Check that path was normalized
                call_args = mock_req.call_args
                assert call_args[0][1] == "/api/test"

    @pytest.mark.asyncio
    async def test_request_normalizes_method_case(self):
        """Request should normalize method to uppercase."""
        client = XHSClient(cookies={"a1": "test_a1_value"})
        async with client:
            with patch.object(
                client._http, "request", new_callable=AsyncMock
            ) as mock_req:
                mock_req.return_value = AsyncMock(
                    status_code=200, json=MagicMock(return_value={"success": True})
                )

                await client._request("get", "/api/test")

                # Check that method was normalized
                call_args = mock_req.call_args
                assert call_args[0][0] == "GET"

    @pytest.mark.asyncio
    async def test_request_success_returns_json(self):
        """Successful request should return parsed JSON."""
        client = XHSClient(cookies={"a1": "test_a1_value"})
        async with client:
            with patch.object(
                client._http, "request", new_callable=AsyncMock
            ) as mock_req:
                expected = {"success": True, "data": {"id": 123}}
                mock_req.return_value = AsyncMock(
                    status_code=200, json=MagicMock(return_value=expected)
                )

                result = await client._request("GET", "/api/test")
                assert result == expected

    @pytest.mark.asyncio
    async def test_request_2xx_range_success(self):
        """Any 2xx status should be treated as success."""
        for status_code in [200, 201, 204, 299]:
            client = XHSClient(cookies={"a1": "test_a1_value"})
            async with client:
                with patch.object(
                    client._http, "request", new_callable=AsyncMock
                ) as mock_req:
                    expected = {"status": status_code}
                    mock_req.return_value = AsyncMock(
                        status_code=status_code, json=MagicMock(return_value=expected)
                    )

                    result = await client._request("GET", "/api/test")
                    assert result == expected

    @pytest.mark.asyncio
    async def test_request_invalid_json_response_raises(self):
        """Non-dict JSON response should raise APIError."""
        client = XHSClient(cookies={"a1": "test_a1_value"})
        async with client:
            with patch.object(
                client._http, "request", new_callable=AsyncMock
            ) as mock_req:
                mock_req.return_value = AsyncMock(
                    status_code=200,
                    json=MagicMock(return_value=[1, 2, 3]),
                    text="[1, 2, 3]",
                )

                with pytest.raises(APIError, match="Invalid JSON response"):
                    await client._request("GET", "/api/test")

    @pytest.mark.asyncio
    async def test_request_http_error_raises_api_error(self):
        """HTTP request error should raise APIError."""
        client = XHSClient(cookies={"a1": "test_a1_value"})
        async with client:
            with patch.object(
                client._http, "request", new_callable=AsyncMock
            ) as mock_req:
                mock_req.side_effect = httpx.RequestError("Connection failed")

                with pytest.raises(APIError, match="Connection failed"):
                    await client._request("GET", "/api/test")

    @pytest.mark.asyncio
    async def test_request_status_461_raises_signature_error(self):
        """Status 461 should raise SignatureError."""
        from xhs_scraper.exceptions import SignatureError

        client = XHSClient(cookies={"a1": "test_a1_value"})
        async with client:
            with patch.object(
                client._http, "request", new_callable=AsyncMock
            ) as mock_req:
                mock_req.return_value = AsyncMock(
                    status_code=461,
                    json=MagicMock(return_value={"message": "Signature expired"}),
                    text="Signature expired",
                )

                with pytest.raises(SignatureError):
                    await client._request("GET", "/api/test")

    @pytest.mark.asyncio
    async def test_request_status_471_raises_captcha_error(self):
        """Status 471 should raise CaptchaRequiredError."""
        from xhs_scraper.exceptions import CaptchaRequiredError

        client = XHSClient(cookies={"a1": "test_a1_value"})
        async with client:
            with patch.object(
                client._http, "request", new_callable=AsyncMock
            ) as mock_req:
                mock_req.return_value = AsyncMock(
                    status_code=471,
                    json=MagicMock(return_value={"message": "Captcha required"}),
                    text="Captcha required",
                )

                with pytest.raises(CaptchaRequiredError):
                    await client._request("GET", "/api/test")

    @pytest.mark.asyncio
    async def test_request_status_429_raises_rate_limit_error(self):
        """Status 429 should raise RateLimitError."""
        from xhs_scraper.exceptions import RateLimitError

        client = XHSClient(cookies={"a1": "test_a1_value"})
        async with client:
            with patch.object(
                client._http, "request", new_callable=AsyncMock
            ) as mock_req:
                mock_req.return_value = AsyncMock(
                    status_code=429,
                    json=MagicMock(return_value={"message": "Too many requests"}),
                    text="Too many requests",
                )

                with pytest.raises(RateLimitError):
                    await client._request("GET", "/api/test")

    @pytest.mark.asyncio
    async def test_request_status_401_raises_cookie_expired_error(self):
        """Status 401 should raise CookieExpiredError."""
        from xhs_scraper.exceptions import CookieExpiredError

        client = XHSClient(cookies={"a1": "test_a1_value"})
        async with client:
            with patch.object(
                client._http, "request", new_callable=AsyncMock
            ) as mock_req:
                mock_req.return_value = AsyncMock(
                    status_code=401,
                    json=MagicMock(return_value={"message": "Unauthorized"}),
                    text="Unauthorized",
                )

                with pytest.raises(CookieExpiredError):
                    await client._request("GET", "/api/test")

    @pytest.mark.asyncio
    async def test_request_status_403_raises_cookie_expired_error(self):
        """Status 403 should raise CookieExpiredError."""
        from xhs_scraper.exceptions import CookieExpiredError

        client = XHSClient(cookies={"a1": "test_a1_value"})
        async with client:
            with patch.object(
                client._http, "request", new_callable=AsyncMock
            ) as mock_req:
                mock_req.return_value = AsyncMock(
                    status_code=403,
                    json=MagicMock(return_value={"message": "Forbidden"}),
                    text="Forbidden",
                )

                with pytest.raises(CookieExpiredError):
                    await client._request("GET", "/api/test")

    @pytest.mark.asyncio
    async def test_request_other_error_status_raises_api_error(self):
        """Other error statuses should raise generic APIError."""
        for status_code in [400, 404, 500, 502, 503]:
            client = XHSClient(cookies={"a1": "test_a1_value"})
            async with client:
                with patch.object(
                    client._http, "request", new_callable=AsyncMock
                ) as mock_req:
                    mock_req.return_value = AsyncMock(
                        status_code=status_code,
                        json=MagicMock(return_value={"error": "Some error"}),
                        text="Some error",
                    )

                    with pytest.raises(APIError) as exc_info:
                        await client._request("GET", "/api/test")

                    assert exc_info.value.status_code == status_code

    @pytest.mark.asyncio
    async def test_request_respects_rate_limiter(self):
        """Request should call rate limiter if configured."""
        client = XHSClient(cookies={"a1": "test_a1_value"}, rate_limit=10.0)
        async with client:
            with patch.object(
                client._rate_limiter, "acquire", new_callable=AsyncMock
            ) as mock_acquire:
                with patch.object(
                    client._http, "request", new_callable=AsyncMock
                ) as mock_req:
                    mock_req.return_value = AsyncMock(
                        status_code=200, json=MagicMock(return_value={"success": True})
                    )

                    await client._request("GET", "/api/test")
                    mock_acquire.assert_called_once()

    @pytest.mark.asyncio
    async def test_request_get_includes_params(self):
        """GET request should include params."""
        client = XHSClient(cookies={"a1": "test_a1_value"})
        async with client:
            with patch.object(
                client._http, "request", new_callable=AsyncMock
            ) as mock_req:
                mock_req.return_value = AsyncMock(
                    status_code=200, json=MagicMock(return_value={"success": True})
                )

                params = {"key": "value"}
                await client._request("GET", "/api/test", params=params)

                call_args = mock_req.call_args
                assert call_args[1]["params"] == params
                assert call_args[1]["json"] is None

    @pytest.mark.asyncio
    async def test_request_post_includes_payload(self):
        """POST request should include JSON payload."""
        client = XHSClient(cookies={"a1": "test_a1_value"})
        async with client:
            with patch.object(
                client._http, "request", new_callable=AsyncMock
            ) as mock_req:
                mock_req.return_value = AsyncMock(
                    status_code=200, json=MagicMock(return_value={"success": True})
                )

                payload = {"key": "value"}
                await client._request("POST", "/api/test", payload=payload)

                call_args = mock_req.call_args
                assert call_args[1]["json"] == payload
                assert call_args[1]["params"] is None

    @pytest.mark.asyncio
    async def test_request_includes_signed_headers(self):
        """Request should include headers from signature provider."""
        client = XHSClient(cookies={"a1": "test_a1_value"})
        async with client:
            mock_signed_headers = {"x-signature": "abc123"}
            client._signature_provider.sign_get = Mock(return_value=mock_signed_headers)

            with patch.object(
                client._http, "request", new_callable=AsyncMock
            ) as mock_req:
                mock_req.return_value = AsyncMock(
                    status_code=200, json=MagicMock(return_value={"success": True})
                )

                await client._request("GET", "/api/test")

                call_args = mock_req.call_args
                headers = call_args[1]["headers"]
                assert headers["x-signature"] == "abc123"

    @pytest.mark.asyncio
    async def test_request_merges_custom_headers(self):
        """Request should merge custom headers with signed headers."""
        client = XHSClient(cookies={"a1": "test_a1_value"})
        async with client:
            mock_signed_headers = {"x-signature": "abc123"}
            client._signature_provider.sign_post = Mock(
                return_value=mock_signed_headers
            )

            with patch.object(
                client._http, "request", new_callable=AsyncMock
            ) as mock_req:
                mock_req.return_value = AsyncMock(
                    status_code=200, json=MagicMock(return_value={"success": True})
                )

                custom_headers = {"x-custom": "value"}
                await client._request("POST", "/api/test", headers=custom_headers)

                call_args = mock_req.call_args
                headers = call_args[1]["headers"]
                assert headers["x-signature"] == "abc123"
                assert headers["x-custom"] == "value"

    @pytest.mark.asyncio
    async def test_request_error_message_extraction_from_message(self):
        """Error message should be extracted from 'message' field."""
        from xhs_scraper.exceptions import RateLimitError

        client = XHSClient(cookies={"a1": "test_a1_value"})
        async with client:
            with patch.object(
                client._http, "request", new_callable=AsyncMock
            ) as mock_req:
                mock_req.return_value = AsyncMock(
                    status_code=429,
                    json=MagicMock(return_value={"message": "Custom error message"}),
                    text="fallback",
                )

                with pytest.raises(RateLimitError) as exc_info:
                    await client._request("GET", "/api/test")

                assert str(exc_info.value) == "Custom error message"


class TestXHSClientBaseUrl:
    """Test BASE_URL constant."""

    def test_base_url_is_correct(self):
        """BASE_URL should point to Xiaohongshu API."""
        assert XHSClient.BASE_URL == "https://edith.xiaohongshu.com"


class TestXHSClientHttpxClientConfiguration:
    """Test httpx client configuration."""

    @pytest.mark.asyncio
    async def test_httpx_client_includes_cookies(self):
        """httpx client should include cookies."""
        cookies = {"session": "abc123", "user": "test"}
        client = XHSClient(cookies=cookies)

        async with client:
            assert client._http.cookies == httpx.Cookies(cookies)

    @pytest.mark.asyncio
    async def test_httpx_client_includes_base_url(self):
        """httpx client should include base URL."""
        client = XHSClient(cookies={"a1": "test_a1_value"})

        async with client:
            assert client._http.base_url == XHSClient.BASE_URL

    @pytest.mark.asyncio
    async def test_httpx_client_includes_timeout(self):
        """httpx client should include timeout."""
        client = XHSClient(cookies={"a1": "test_a1_value"}, timeout=60.0)

        async with client:
            assert client._http.timeout.read == 60.0

    @pytest.mark.asyncio
    async def test_httpx_client_includes_headers(self):
        """httpx client should include required headers."""
        client = XHSClient(cookies={"a1": "test_a1_value"})

        async with client:
            headers = client._http.headers
            assert headers["accept"] == "application/json, text/plain, */*"
            assert headers["content-type"] == "application/json;charset=UTF-8"
            assert headers["origin"] == "https://www.xiaohongshu.com"
            assert headers["referer"] == "https://www.xiaohongshu.com/"

    @pytest.mark.asyncio
    async def test_httpx_client_follow_redirects(self):
        """httpx client should follow redirects."""
        client = XHSClient(cookies={"a1": "test_a1_value"})

        async with client:
            assert client._http.follow_redirects is True
