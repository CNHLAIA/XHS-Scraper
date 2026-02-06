"""Search scraper for Xiaohongshu (XHS).

This module provides SearchScraper for searching notes on XHS using
keyword-based search with page-based pagination.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Optional

from xhs_scraper.models import SearchResultResponse

if TYPE_CHECKING:
    from xhs_scraper.client import XHSClient


# Note type mapping: string to integer for API
NOTE_TYPE_MAP = {
    "ALL": 0,
    "VIDEO": 1,
    "IMAGE": 2,
}


class SearchScraper:
    """Scraper for searching notes on XHS."""

    def __init__(self, client: XHSClient):
        """Initialize SearchScraper with an XHS client.

        Args:
            client: XHSClient instance for making API requests.
        """
        self._client = client

    async def search_notes(
        self,
        keyword: str,
        page: int = 1,
        page_size: int = 20,
        sort: Literal["GENERAL", "TIME_DESC", "POPULARITY"] = "GENERAL",
        note_type: Literal["ALL", "VIDEO", "IMAGE"] = "ALL",
    ) -> SearchResultResponse:
        """Search for notes by keyword.

        Args:
            keyword: Search keyword.
            page: Page number (1-indexed, default 1).
            page_size: Number of results per page (max 20, default 20).
            sort: Sort order - "GENERAL", "TIME_DESC", or "POPULARITY" (default "GENERAL").
            note_type: Filter by note type - "ALL", "VIDEO", or "IMAGE" (default "ALL").

        Returns:
            SearchResultResponse containing note items and pagination info.

        Raises:
            APIError: If the request fails.
            SignatureError: If request signing fails.
            CaptchaRequiredError: If CAPTCHA is required.
            RateLimitError: If rate limited.
            CookieExpiredError: If cookies are expired.
        """
        # Normalize page_size to max 20
        normalized_page_size = min(page_size, 20)

        payload = {
            "keyword": keyword,
            "page": page,
            "page_size": normalized_page_size,
            "search_id": "",
            "sort": sort,
            "note_type": NOTE_TYPE_MAP.get(note_type, 0),
        }

        response_data = await self._client._request(
            "POST",
            "/api/sns/web/v1/search/notes",
            payload=payload,
        )

        # Parse response
        items_data = response_data.get("items", [])
        items = []
        for item_data in items_data:
            try:
                # Extract note data from item
                note_data = item_data.get("note_card", {})
                from xhs_scraper.models import NoteResponse

                note = NoteResponse(**note_data)
                items.append(note)
            except Exception:
                # Skip malformed note data
                pass

        return SearchResultResponse(
            items=items,
            has_more=response_data.get("has_more", False),
            cursor=response_data.get("cursor", ""),
        )


__all__ = ["SearchScraper"]
