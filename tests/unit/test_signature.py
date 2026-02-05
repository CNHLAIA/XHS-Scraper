"""Unit tests for xhs_scraper.signature module."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from xhs_scraper.signature import XHShowSignatureProvider, SignatureProvider


class TestSignatureProviderProtocol:
    """Test SignatureProvider protocol definition."""

    def test_signature_provider_has_sign_get_method(self):
        """SignatureProvider protocol defines sign_get method."""
        assert hasattr(SignatureProvider, "sign_get")

    def test_signature_provider_has_sign_post_method(self):
        """SignatureProvider protocol defines sign_post method."""
        assert hasattr(SignatureProvider, "sign_post")


class TestXHShowSignatureProviderInit:
    """Test XHShowSignatureProvider initialization."""

    @patch("xhs_scraper.signature.Xhshow")
    @patch("xhs_scraper.signature.SessionManager")
    def test_init_creates_client_and_session(self, mock_session_manager, mock_xhshow):
        """Initialization creates Xhshow client and SessionManager."""
        provider = XHShowSignatureProvider()

        assert provider._client is not None
        assert provider._session is not None
        mock_xhshow.assert_called_once()
        mock_session_manager.assert_called_once()


class TestXHShowSignatureProviderSignGet:
    """Test XHShowSignatureProvider.sign_get() method."""

    @patch("xhs_scraper.signature.Xhshow")
    @patch("xhs_scraper.signature.SessionManager")
    def test_sign_get_with_uri_only(self, mock_session_manager, mock_xhshow):
        """sign_get with only URI."""
        mock_client = MagicMock()
        mock_xhshow.return_value = mock_client
        mock_client.sign_headers_get.return_value = {
            "x-s": "signature_value",
            "x-t": "timestamp",
        }

        provider = XHShowSignatureProvider()
        headers = provider.sign_get("/api/endpoint")

        mock_client.sign_headers_get.assert_called_once()
        call_kwargs = mock_client.sign_headers_get.call_args.kwargs
        assert call_kwargs["uri"] == "/api/endpoint"
        assert call_kwargs["params"] == {}
        assert call_kwargs["cookies"] == {}
        assert "x-s" in headers

    @patch("xhs_scraper.signature.Xhshow")
    @patch("xhs_scraper.signature.SessionManager")
    def test_sign_get_with_params(self, mock_session_manager, mock_xhshow):
        """sign_get with URI and parameters."""
        mock_client = MagicMock()
        mock_xhshow.return_value = mock_client
        mock_client.sign_headers_get.return_value = {"x-s": "signature"}

        provider = XHShowSignatureProvider()
        params = {"search": "test", "page": 1}
        headers = provider.sign_get("/api/search", params=params)

        call_kwargs = mock_client.sign_headers_get.call_args.kwargs
        assert call_kwargs["params"] == params

    @patch("xhs_scraper.signature.Xhshow")
    @patch("xhs_scraper.signature.SessionManager")
    def test_sign_get_with_cookies(self, mock_session_manager, mock_xhshow):
        """sign_get with URI and cookies."""
        mock_client = MagicMock()
        mock_xhshow.return_value = mock_client
        mock_client.sign_headers_get.return_value = {"x-s": "signature"}

        provider = XHShowSignatureProvider()
        cookies = {"sessionid": "abc123"}
        headers = provider.sign_get("/api/endpoint", cookies=cookies)

        call_kwargs = mock_client.sign_headers_get.call_args.kwargs
        assert call_kwargs["cookies"] == cookies

    @patch("xhs_scraper.signature.Xhshow")
    @patch("xhs_scraper.signature.SessionManager")
    def test_sign_get_with_all_parameters(self, mock_session_manager, mock_xhshow):
        """sign_get with URI, params, and cookies."""
        mock_client = MagicMock()
        mock_xhshow.return_value = mock_client
        expected_headers = {
            "x-s": "sig123",
            "x-s-common": "common_sig",
            "x-t": "1234567890",
        }
        mock_client.sign_headers_get.return_value = expected_headers

        provider = XHShowSignatureProvider()
        params = {"keyword": "test"}
        cookies = {"user": "test_user"}

        headers = provider.sign_get("/api/search", params=params, cookies=cookies)

        assert headers == expected_headers
        call_kwargs = mock_client.sign_headers_get.call_args.kwargs
        assert call_kwargs["uri"] == "/api/search"
        assert call_kwargs["params"] == params
        assert call_kwargs["cookies"] == cookies

    @patch("xhs_scraper.signature.Xhshow")
    @patch("xhs_scraper.signature.SessionManager")
    def test_sign_get_defaults_none_params_to_empty_dict(
        self, mock_session_manager, mock_xhshow
    ):
        """sign_get converts None params to empty dict."""
        mock_client = MagicMock()
        mock_xhshow.return_value = mock_client
        mock_client.sign_headers_get.return_value = {"x-s": "sig"}

        provider = XHShowSignatureProvider()
        provider.sign_get("/api/endpoint", params=None)

        call_kwargs = mock_client.sign_headers_get.call_args.kwargs
        assert call_kwargs["params"] == {}

    @patch("xhs_scraper.signature.Xhshow")
    @patch("xhs_scraper.signature.SessionManager")
    def test_sign_get_defaults_none_cookies_to_empty_dict(
        self, mock_session_manager, mock_xhshow
    ):
        """sign_get converts None cookies to empty dict."""
        mock_client = MagicMock()
        mock_xhshow.return_value = mock_client
        mock_client.sign_headers_get.return_value = {"x-s": "sig"}

        provider = XHShowSignatureProvider()
        provider.sign_get("/api/endpoint", cookies=None)

        call_kwargs = mock_client.sign_headers_get.call_args.kwargs
        assert call_kwargs["cookies"] == {}


class TestXHShowSignatureProviderSignPost:
    """Test XHShowSignatureProvider.sign_post() method."""

    @patch("xhs_scraper.signature.Xhshow")
    @patch("xhs_scraper.signature.SessionManager")
    def test_sign_post_with_uri_only(self, mock_session_manager, mock_xhshow):
        """sign_post with only URI."""
        mock_client = MagicMock()
        mock_xhshow.return_value = mock_client
        mock_client.sign_headers_post.return_value = {
            "x-s": "signature_value",
            "x-t": "timestamp",
        }

        provider = XHShowSignatureProvider()
        headers = provider.sign_post("/api/endpoint")

        mock_client.sign_headers_post.assert_called_once()
        call_kwargs = mock_client.sign_headers_post.call_args.kwargs
        assert call_kwargs["uri"] == "/api/endpoint"
        assert call_kwargs["payload"] == {}
        assert call_kwargs["cookies"] == {}

    @patch("xhs_scraper.signature.Xhshow")
    @patch("xhs_scraper.signature.SessionManager")
    def test_sign_post_with_payload(self, mock_session_manager, mock_xhshow):
        """sign_post with URI and payload."""
        mock_client = MagicMock()
        mock_xhshow.return_value = mock_client
        mock_client.sign_headers_post.return_value = {"x-s": "signature"}

        provider = XHShowSignatureProvider()
        payload = {"query": "test search", "offset": 0}
        headers = provider.sign_post("/api/search", payload=payload)

        call_kwargs = mock_client.sign_headers_post.call_args.kwargs
        assert call_kwargs["payload"] == payload

    @patch("xhs_scraper.signature.Xhshow")
    @patch("xhs_scraper.signature.SessionManager")
    def test_sign_post_with_cookies(self, mock_session_manager, mock_xhshow):
        """sign_post with URI and cookies."""
        mock_client = MagicMock()
        mock_xhshow.return_value = mock_client
        mock_client.sign_headers_post.return_value = {"x-s": "signature"}

        provider = XHShowSignatureProvider()
        cookies = {"sessionid": "xyz789"}
        headers = provider.sign_post("/api/endpoint", cookies=cookies)

        call_kwargs = mock_client.sign_headers_post.call_args.kwargs
        assert call_kwargs["cookies"] == cookies

    @patch("xhs_scraper.signature.Xhshow")
    @patch("xhs_scraper.signature.SessionManager")
    def test_sign_post_with_all_parameters(self, mock_session_manager, mock_xhshow):
        """sign_post with URI, payload, and cookies."""
        mock_client = MagicMock()
        mock_xhshow.return_value = mock_client
        expected_headers = {
            "x-s": "post_sig",
            "x-s-common": "common_sig",
            "x-t": "9876543210",
        }
        mock_client.sign_headers_post.return_value = expected_headers

        provider = XHShowSignatureProvider()
        payload = {"data": "value"}
        cookies = {"auth": "token"}

        headers = provider.sign_post("/api/post", payload=payload, cookies=cookies)

        assert headers == expected_headers
        call_kwargs = mock_client.sign_headers_post.call_args.kwargs
        assert call_kwargs["uri"] == "/api/post"
        assert call_kwargs["payload"] == payload
        assert call_kwargs["cookies"] == cookies

    @patch("xhs_scraper.signature.Xhshow")
    @patch("xhs_scraper.signature.SessionManager")
    def test_sign_post_defaults_none_payload_to_empty_dict(
        self, mock_session_manager, mock_xhshow
    ):
        """sign_post converts None payload to empty dict."""
        mock_client = MagicMock()
        mock_xhshow.return_value = mock_client
        mock_client.sign_headers_post.return_value = {"x-s": "sig"}

        provider = XHShowSignatureProvider()
        provider.sign_post("/api/endpoint", payload=None)

        call_kwargs = mock_client.sign_headers_post.call_args.kwargs
        assert call_kwargs["payload"] == {}

    @patch("xhs_scraper.signature.Xhshow")
    @patch("xhs_scraper.signature.SessionManager")
    def test_sign_post_defaults_none_cookies_to_empty_dict(
        self, mock_session_manager, mock_xhshow
    ):
        """sign_post converts None cookies to empty dict."""
        mock_client = MagicMock()
        mock_xhshow.return_value = mock_client
        mock_client.sign_headers_post.return_value = {"x-s": "sig"}

        provider = XHShowSignatureProvider()
        provider.sign_post("/api/endpoint", cookies=None)

        call_kwargs = mock_client.sign_headers_post.call_args.kwargs
        assert call_kwargs["cookies"] == {}


class TestXHShowSignatureProviderHeaderFormats:
    """Test that returned headers have expected structure."""

    @patch("xhs_scraper.signature.Xhshow")
    @patch("xhs_scraper.signature.SessionManager")
    def test_sign_get_returns_dict(self, mock_session_manager, mock_xhshow):
        """sign_get returns dictionary."""
        mock_client = MagicMock()
        mock_xhshow.return_value = mock_client
        mock_client.sign_headers_get.return_value = {
            "x-s": "signature",
            "x-t": "timestamp",
        }

        provider = XHShowSignatureProvider()
        headers = provider.sign_get("/api/endpoint")

        assert isinstance(headers, dict)

    @patch("xhs_scraper.signature.Xhshow")
    @patch("xhs_scraper.signature.SessionManager")
    def test_sign_post_returns_dict(self, mock_session_manager, mock_xhshow):
        """sign_post returns dictionary."""
        mock_client = MagicMock()
        mock_xhshow.return_value = mock_client
        mock_client.sign_headers_post.return_value = {
            "x-s": "signature",
            "x-t": "timestamp",
        }

        provider = XHShowSignatureProvider()
        headers = provider.sign_post("/api/endpoint")

        assert isinstance(headers, dict)


class TestSignatureProviderUsesSessionManager:
    """Test that provider correctly uses SessionManager."""

    @patch("xhs_scraper.signature.Xhshow")
    @patch("xhs_scraper.signature.SessionManager")
    def test_sign_get_passes_session_to_client(self, mock_session_manager, mock_xhshow):
        """sign_get passes session to xhshow client."""
        mock_client = MagicMock()
        mock_session = MagicMock()
        mock_xhshow.return_value = mock_client
        mock_session_manager.return_value = mock_session
        mock_client.sign_headers_get.return_value = {"x-s": "sig"}

        provider = XHShowSignatureProvider()
        provider.sign_get("/api/endpoint")

        call_kwargs = mock_client.sign_headers_get.call_args.kwargs
        assert call_kwargs["session"] is mock_session

    @patch("xhs_scraper.signature.Xhshow")
    @patch("xhs_scraper.signature.SessionManager")
    def test_sign_post_passes_session_to_client(
        self, mock_session_manager, mock_xhshow
    ):
        """sign_post passes session to xhshow client."""
        mock_client = MagicMock()
        mock_session = MagicMock()
        mock_xhshow.return_value = mock_client
        mock_session_manager.return_value = mock_session
        mock_client.sign_headers_post.return_value = {"x-s": "sig"}

        provider = XHShowSignatureProvider()
        provider.sign_post("/api/endpoint")

        call_kwargs = mock_client.sign_headers_post.call_args.kwargs
        assert call_kwargs["session"] is mock_session

    @patch("xhs_scraper.signature.Xhshow")
    @patch("xhs_scraper.signature.SessionManager")
    def test_provider_reuses_same_session(self, mock_session_manager, mock_xhshow):
        """Provider reuses same session for multiple calls."""
        mock_client = MagicMock()
        mock_session = MagicMock()
        mock_xhshow.return_value = mock_client
        mock_session_manager.return_value = mock_session
        mock_client.sign_headers_get.return_value = {"x-s": "sig"}
        mock_client.sign_headers_post.return_value = {"x-s": "sig"}

        provider = XHShowSignatureProvider()
        provider.sign_get("/api/get")
        provider.sign_post("/api/post")

        assert mock_session_manager.call_count == 1

        get_session = mock_client.sign_headers_get.call_args.kwargs["session"]
        post_session = mock_client.sign_headers_post.call_args.kwargs["session"]
        assert get_session is post_session
