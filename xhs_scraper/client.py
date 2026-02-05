"""Async API client for Xiaohongshu (XHS).

This module defines XHSClient, the core HTTP client used by scraper modules.
The client:
- owns an internal httpx.AsyncClient (async context manager)
- signs requests via SignatureProvider (xhshow abstraction)
- optionally rate limits requests via TokenBucketRateLimiter
"""

from __future__ import annotations

from dataclasses import dataclass
import importlib
from typing import Any, Dict, Mapping, Optional

import httpx

from .exceptions import (
    APIError,
    CaptchaRequiredError,
    CookieExpiredError,
    RateLimitError,
    SignatureError,
)
from .signature import SignatureProvider, XHShowSignatureProvider
from .utils.rate_limiter import TokenBucketRateLimiter


def _normalize_path(path: str) -> str:
    if not path:
        raise ValueError("path must be non-empty")
    return path if path.startswith("/") else f"/{path}"


def _extract_error_message(payload: Any, fallback: str) -> str:
    if isinstance(payload, dict):
        for key in ("message", "msg", "error", "error_message"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value
    return fallback


@dataclass(frozen=True)
class _Scrapers:
    notes: Any
    users: Any
    comments: Any
    search: Any


class XHSClient:
    """Async context manager owning an internal httpx.AsyncClient."""

    BASE_URL = "https://edith.xiaohongshu.com"

    def __init__(
        self,
        *,
        cookies: Mapping[str, str],
        rate_limit: Optional[float] = None,
        signature_provider: Optional[SignatureProvider] = None,
        timeout: float = 30.0,
    ):
        if not isinstance(cookies, Mapping) or not cookies:
            raise ValueError("cookies must be a non-empty mapping")

        if rate_limit is not None and rate_limit <= 0:
            raise ValueError("rate_limit must be positive")

        self.cookies: Dict[str, str] = dict(cookies)
        self._timeout = timeout
        self._signature_provider = signature_provider or XHShowSignatureProvider()
        self._rate_limiter = (
            TokenBucketRateLimiter(rate=rate_limit) if rate_limit is not None else None
        )

        self._http: Optional[httpx.AsyncClient] = None

        # Attach scrapers (real implementations may be provided later).
        notes_cls = _load_scraper_class("scrapers.note", "NoteScraper", _NotesScraper)
        users_cls = _load_scraper_class("scrapers.user", "UserScraper", _UsersScraper)
        comments_cls = _load_scraper_class(
            "scrapers.comment", "CommentScraper", _CommentsScraper
        )
        search_cls = _load_scraper_class(
            "scrapers.search", "SearchScraper", _SearchScraper
        )

        self._scrapers = _Scrapers(
            notes=notes_cls(self),
            users=users_cls(self),
            comments=comments_cls(self),
            search=search_cls(self),
        )

    async def __aenter__(self) -> "XHSClient":
        if self._http is None:
            self._http = httpx.AsyncClient(
                base_url=self.BASE_URL,
                timeout=self._timeout,
                cookies=self.cookies,
                headers={
                    "accept": "application/json, text/plain, */*",
                    "content-type": "application/json;charset=UTF-8",
                    "origin": "https://www.xiaohongshu.com",
                    "referer": "https://www.xiaohongshu.com/",
                },
                follow_redirects=True,
            )
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self._http is None:
            return
        await self._http.aclose()
        self._http = None

    @property
    def notes(self) -> Any:
        return self._scrapers.notes

    @property
    def users(self) -> Any:
        return self._scrapers.users

    @property
    def comments(self) -> Any:
        return self._scrapers.comments

    @property
    def search(self) -> Any:
        return self._scrapers.search

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        payload: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make a signed request to XHS API.

        Args:
            method: "GET" or "POST"
            path: API path (e.g. "/api/sns/web/v1/feed")
            params: Querystring parameters for GET requests
            payload: JSON body for POST requests
            headers: Extra headers to merge into the request

        Returns:
            Parsed JSON response (dict)

        Raises:
            SignatureError: HTTP 461
            CaptchaRequiredError: HTTP 471
            RateLimitError: HTTP 429
            CookieExpiredError: HTTP 401/403
            APIError: any other non-2xx status or invalid JSON
        """
        if self._http is None:
            raise RuntimeError("XHSClient must be used as an async context manager")

        normalized_method = method.upper().strip()
        if normalized_method not in {"GET", "POST"}:
            raise ValueError("method must be GET or POST")

        uri = _normalize_path(path)
        params = params or {}
        payload = payload or {}

        if self._rate_limiter is not None:
            await self._rate_limiter.acquire()

        signed_headers: Dict[str, str]
        if normalized_method == "GET":
            signed_headers = self._signature_provider.sign_get(
                uri=uri, params=params, cookies=self.cookies
            )
        else:
            signed_headers = self._signature_provider.sign_post(
                uri=uri, payload=payload, cookies=self.cookies
            )

        merged_headers: Dict[str, str] = dict(signed_headers)
        if headers:
            merged_headers.update(headers)

        try:
            response = await self._http.request(
                normalized_method,
                uri,
                params=params if normalized_method == "GET" else None,
                json=payload if normalized_method == "POST" else None,
                headers=merged_headers,
            )
        except httpx.RequestError as exc:
            raise APIError(status_code=0, message=str(exc), response_data=None) from exc

        response_payload: Any
        try:
            response_payload = response.json()
        except ValueError:
            response_payload = None

        if 200 <= response.status_code < 300:
            if not isinstance(response_payload, dict):
                raise APIError(
                    status_code=response.status_code,
                    message="Invalid JSON response",
                    response_data={"text": response.text},
                )
            return response_payload

        message = _extract_error_message(response_payload, fallback=response.text)
        status = response.status_code

        if status == 461:
            raise SignatureError(message)
        if status == 471:
            raise CaptchaRequiredError(message)
        if status == 429:
            raise RateLimitError(message)
        if status in (401, 403):
            raise CookieExpiredError(message)

        raise APIError(
            status_code=status, message=message, response_data=response_payload
        )

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        payload: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Public API for making signed requests to XHS API.

        This is the public interface to _request(). Delegates all calls to _request().

        Args:
            method: "GET" or "POST"
            path: API path (e.g. "/api/sns/web/v1/feed")
            params: Querystring parameters for GET requests
            payload: JSON body for POST requests
            headers: Extra headers to merge into the request

        Returns:
            Parsed JSON response (dict)

        Raises:
            SignatureError: HTTP 461
            CaptchaRequiredError: HTTP 471
            RateLimitError: HTTP 429
            CookieExpiredError: HTTP 401/403
            APIError: any other non-2xx status or invalid JSON
        """
        return await self._request(
            method=method,
            path=path,
            params=params,
            payload=payload,
            headers=headers,
        )


class _NotesScraper:
    def __init__(self, client: XHSClient):
        self._client = client


class _UsersScraper:
    def __init__(self, client: XHSClient):
        self._client = client


class _CommentsScraper:
    def __init__(self, client: XHSClient):
        self._client = client


class _SearchScraper:
    def __init__(self, client: XHSClient):
        self._client = client


def _load_scraper_class(module_suffix: str, class_name: str, fallback: Any) -> Any:
    """Attempt to import scraper class; return fallback if unavailable."""
    module_name = f"{__package__}.{module_suffix}" if __package__ else module_suffix
    try:
        module = importlib.import_module(module_name)
    except Exception:
        return fallback

    scraper_cls = getattr(module, class_name, None)
    return scraper_cls if scraper_cls is not None else fallback


__all__ = ["XHSClient"]
