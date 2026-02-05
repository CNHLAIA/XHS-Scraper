"""NoteScraper for Xiaohongshu notes (posts).

This module provides NoteScraper class for:
- Fetching individual notes via get_note()
- Fetching user's posted notes via get_user_notes() with cursor-based pagination
"""

from typing import Dict, Any, Optional, List, Set
from ..models import NoteResponse, PaginatedResponse
from ..client import XHSClient


class NoteScraper:
    """Scraper for Xiaohongshu notes/posts."""

    def __init__(self, client: XHSClient):
        """Initialize NoteScraper with client reference.

        Args:
            client: XHSClient instance for making API requests
        """
        self._client = client

    async def get_note(self, note_id: str, xsec_token: str) -> NoteResponse:
        """Fetch a single note by ID.

        Args:
            note_id: The note ID to fetch
            xsec_token: Security token required for the request

        Returns:
            NoteResponse object containing note data

        Raises:
            APIError: If the API request fails
            SignatureError: If request signature validation fails
            CaptchaRequiredError: If CAPTCHA verification is required
            RateLimitError: If rate limit is exceeded
            CookieExpiredError: If authentication cookies are expired
        """
        payload = {
            "source_type": "user_posted",
            "image_formats": ["jpg", "webp", "avif"],
            "note_index": 0,
            "cursor": "",
            "num": 30,
            "refresh_type": 1,
            "note_id": note_id,
            "unread_begin_note_id": "",
            "unread_end_note_id": "",
            "unread_note_count": 0,
            "category": "homefeed_recommend",
        }

        response_data = await self._client._request(
            method="POST",
            path="/api/sns/web/v1/feed",
            payload=payload,
            headers={"X-b3-traceid": xsec_token},
        )

        # Extract note from feed response
        items = response_data.get("data", {}).get("items", [])
        if items:
            note_card = items[0].get("note_card", {})
            return NoteResponse(**note_card)

        return NoteResponse()

    async def get_user_notes(
        self,
        user_id: str,
        cursor: str = "",
        max_pages: int = 100,
    ) -> PaginatedResponse[NoteResponse]:
        """Fetch user's posted notes with cursor-based pagination.

        Implements cursor-based pagination with duplicate detection to handle
        edge cases where API returns overlapping results between pages.

        Args:
            user_id: The user ID whose notes to fetch
            cursor: Pagination cursor (empty string starts from beginning)
            max_pages: Maximum number of pages to fetch (default 100)

        Returns:
            PaginatedResponse containing list of NoteResponse objects,
            cursor for next page, and has_more flag

        Raises:
            APIError: If the API request fails
            SignatureError: If request signature validation fails
            CaptchaRequiredError: If CAPTCHA verification is required
            RateLimitError: If rate limit is exceeded
            CookieExpiredError: If authentication cookies are expired
        """
        all_notes: List[NoteResponse] = []
        seen_note_ids: Set[str] = set()
        current_cursor = cursor
        pages_fetched = 0

        while pages_fetched < max_pages:
            params = {
                "num": 30,
                "cursor": current_cursor,
                "user_id": user_id,
            }

            response_data = await self._client._request(
                method="GET",
                path="/api/sns/web/v1/user_posted",
                params=params,
            )

            # Extract items and cursor from response
            items = response_data.get("data", {}).get("items", [])
            next_cursor = response_data.get("data", {}).get("cursor", "")
            has_more = response_data.get("data", {}).get("has_more", False)

            # Process notes with duplicate detection
            page_notes = []
            for item in items:
                note_card = item.get("note_card", {})
                note_id = note_card.get("note_id")

                # Skip duplicates
                if note_id and note_id in seen_note_ids:
                    continue

                if note_id:
                    seen_note_ids.add(note_id)

                note_response = NoteResponse(**note_card)
                page_notes.append(note_response)

            all_notes.extend(page_notes)
            pages_fetched += 1

            # Stop if no more pages or cursor hasn't changed
            if not has_more or not next_cursor or next_cursor == current_cursor:
                break

            current_cursor = next_cursor

        return PaginatedResponse(
            items=all_notes,
            cursor=current_cursor,
            has_more=False,  # We've exhausted all pages up to max_pages
        )


__all__ = ["NoteScraper"]
