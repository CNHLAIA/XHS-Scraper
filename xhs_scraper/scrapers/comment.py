"""Comment scraper for Xiaohongshu (XHS).

This module provides CommentScraper for fetching comments and sub-comments
from XHS notes using cursor-based pagination.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from xhs_scraper.models import CommentResponse, PaginatedResponse

if TYPE_CHECKING:
    from xhs_scraper.client import XHSClient


class CommentScraper:
    """Scraper for fetching comments from XHS notes."""

    def __init__(self, client: XHSClient):
        """Initialize CommentScraper with an XHS client.

        Args:
            client: XHSClient instance for making API requests.
        """
        self._client = client

    async def get_comments(
        self,
        note_id: str,
        cursor: str = "",
        max_pages: int = 100,
    ) -> PaginatedResponse[CommentResponse]:
        """Fetch comments for a note with cursor pagination.

        Args:
            note_id: The ID of the note to fetch comments for.
            cursor: Pagination cursor (empty string for first page).
            max_pages: Maximum number of pages to fetch (default 100).

        Returns:
            PaginatedResponse containing comment items and next cursor.

        Raises:
            APIError: If the request fails.
            SignatureError: If request signing fails.
            CaptchaRequiredError: If CAPTCHA is required.
            RateLimitError: If rate limited.
            CookieExpiredError: If cookies are expired.
        """
        seen_cursors: set[str] = set()
        all_comments: List[CommentResponse] = []
        current_cursor = cursor
        page_count = 0

        while page_count < max_pages:
            # Detect duplicate cursor (end of pagination)
            if current_cursor in seen_cursors:
                break

            seen_cursors.add(current_cursor)

            # Make API request
            payload = {
                "note_id": note_id,
                "cursor": current_cursor,
            }
            response_data = await self._client._request(
                "POST",
                "/api/sns/web/v2/comment/page",
                payload=payload,
            )

            # Parse response
            items = response_data.get("items", [])
            for item_data in items:
                try:
                    comment = CommentResponse(**item_data)
                    all_comments.append(comment)
                except Exception:
                    # Skip malformed comment data
                    pass

            # Check for more pages
            current_cursor = response_data.get("cursor", "")
            has_more = response_data.get("has_more", False)

            page_count += 1

            if not has_more or not current_cursor:
                break

        return PaginatedResponse[CommentResponse](
            items=all_comments,
            cursor=current_cursor,
            has_more=False,
        )

    async def get_sub_comments(
        self,
        note_id: str,
        root_comment_id: str,
        cursor: str = "",
    ) -> PaginatedResponse[CommentResponse]:
        """Fetch sub-comments (replies) for a root comment.

        Args:
            note_id: The ID of the note.
            root_comment_id: The ID of the root comment to fetch sub-comments for.
            cursor: Pagination cursor (empty string for first page).

        Returns:
            PaginatedResponse containing sub-comment items and next cursor.

        Raises:
            APIError: If the request fails.
            SignatureError: If request signing fails.
            CaptchaRequiredError: If CAPTCHA is required.
            RateLimitError: If rate limited.
            CookieExpiredError: If cookies are expired.
        """
        payload = {
            "note_id": note_id,
            "root_comment_id": root_comment_id,
            "cursor": cursor,
        }
        response_data = await self._client._request(
            "POST",
            "/api/sns/web/v2/comment/sub/page",
            payload=payload,
        )

        # Parse response
        items = response_data.get("items", [])
        comments: List[CommentResponse] = []
        for item_data in items:
            try:
                comment = CommentResponse(**item_data)
                comments.append(comment)
            except Exception:
                # Skip malformed comment data
                pass

        return PaginatedResponse[CommentResponse](
            items=comments,
            cursor=response_data.get("cursor", ""),
            has_more=response_data.get("has_more", False),
        )


__all__ = ["CommentScraper"]
