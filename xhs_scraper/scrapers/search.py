"""Search scraper for Xiaohongshu (XHS).

This module provides SearchScraper for searching notes on XHS using
keyword-based search with page-based pagination.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Optional
import time
import random
from pprint import pformat

from xhs_scraper.models import SearchResultResponse

if TYPE_CHECKING:
    from xhs_scraper.client import XHSClient


# Note type mapping: string to integer for API
NOTE_TYPE_MAP = {
    "ALL": 0,
    "VIDEO": 1,
    "IMAGE": 2,
}

# Sort type mapping: user-friendly to API format
SORT_TYPE_MAP = {
    "GENERAL": "general",
    "TIME_DESC": "time_descending",
    "POPULARITY": "popularity_descending",
}


def _base36_encode(number: int) -> str:
    """Encode a number to base36 string."""
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
    if number == 0:
        return "0"
    result = []
    while number:
        number, remainder = divmod(number, 36)
        result.append(alphabet[remainder])
    return "".join(reversed(result))


def _generate_search_id() -> str:
    """Generate a unique search_id for API requests."""
    e = int(time.time() * 1000) << 64
    t = int(random.uniform(0, 2147483646))
    return _base36_encode(e + t)


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
            "search_id": _generate_search_id(),
            "sort": SORT_TYPE_MAP.get(sort, "general"),
            "note_type": NOTE_TYPE_MAP.get(note_type, 0),
        }

        response_data = await self._client._request(
            "POST",
            "/api/sns/web/v1/search/notes",
            payload=payload,
        )

        # Parse response
        data = response_data.get("data", {})
        items_data = data.get("items", [])
        items = []
        for item_data in items_data:
            try:
                # Extract note data from item
                note_data = item_data.get("note_card", {})
                if note_data:
                    print("DEBUG note_card:", pformat(note_data))

                interact_info = note_data.get("interact_info") or {}
                stats = note_data.get("stats") or interact_info

                image_list = (
                    note_data.get("image_list") or note_data.get("images") or []
                )
                images = None
                if isinstance(image_list, list):
                    image_urls = []
                    for image in image_list:
                        if isinstance(image, str):
                            image_urls.append(image)
                            continue
                        if isinstance(image, dict):
                            url = (
                                image.get("url")
                                or image.get("url_default")
                                or image.get("url_pre")
                            )
                            if url:
                                image_urls.append(url)
                    if image_urls:
                        images = image_urls

                video_data = (
                    note_data.get("video")
                    or note_data.get("video_info")
                    or note_data.get("video_info_v2")
                )
                if isinstance(video_data, dict):
                    video = (
                        video_data.get("url")
                        or video_data.get("default_url")
                        or video_data.get("master_url")
                    )
                elif isinstance(video_data, str):
                    video = video_data
                else:
                    video = None

                from xhs_scraper.models import NoteResponse

                note = NoteResponse(
                    note_id=note_data.get("note_id") or note_data.get("id"),
                    title=note_data.get("title"),
                    desc=note_data.get("desc"),
                    images=images,
                    video=video,
                    user=note_data.get("user"),
                    stats=stats,
                    liked_count=(
                        interact_info.get("liked_count")
                        or interact_info.get("like_count")
                        or stats.get("liked_count")
                        or stats.get("like_count")
                    ),
                    commented_count=(
                        interact_info.get("comment_count")
                        or interact_info.get("commented_count")
                        or stats.get("comment_count")
                        or stats.get("commented_count")
                    ),
                    shared_count=(
                        interact_info.get("share_count")
                        or interact_info.get("shared_count")
                        or stats.get("share_count")
                        or stats.get("shared_count")
                    ),
                )
                items.append(note)
            except Exception:
                # Skip malformed note data
                pass

        return SearchResultResponse(
            items=items,
            has_more=data.get("has_more", False),
            cursor=data.get("cursor", ""),
        )


__all__ = ["SearchScraper"]
