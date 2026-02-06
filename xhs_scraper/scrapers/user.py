"""User scraper for Xiaohongshu (XHS) API."""

from typing import TYPE_CHECKING, Optional

from ..models import UserResponse

if TYPE_CHECKING:
    from ..client import XHSClient


class UserScraper:
    """Scraper for user-related endpoints."""

    def __init__(self, client: "XHSClient"):
        """Initialize UserScraper with client reference.

        Args:
            client: XHSClient instance for making requests.
        """
        self._client = client

    async def get_user_info(self, user_id: str) -> UserResponse:
        """Get information about another user.

        Args:
            user_id: The target user's ID.

        Returns:
            UserResponse: User information model with fields like nickname, avatar, bio, etc.
                Missing fields are handled gracefully and set to None.

        Raises:
            CookieExpiredError: If authentication cookies are expired.
            SignatureError: If request signature validation fails.
            CaptchaRequiredError: If CAPTCHA verification is required.
            RateLimitError: If API rate limit is exceeded.
            APIError: For other API errors.
        """
        response_data = await self._client._request(
            method="GET",
            path="/api/sns/web/v1/user/otherinfo",
            params={"target_user_id": user_id},
        )

        # Extract user data from response, handling nested structure
        user_data = response_data.get("data", {}) or {}
        if not isinstance(user_data, dict):
            user_data = {}

        return UserResponse(**user_data)

    async def get_self_info(self) -> UserResponse:
        """Get information about the authenticated user (self).

        Returns:
            UserResponse: Current user's information model.
                Missing fields are handled gracefully and set to None.

        Raises:
            CookieExpiredError: If authentication cookies are expired.
            SignatureError: If request signature validation fails.
            CaptchaRequiredError: If CAPTCHA verification is required.
            RateLimitError: If API rate limit is exceeded.
            APIError: For other API errors.
        """
        response_data = await self._client._request(
            method="GET",
            path="/api/sns/web/v1/user/selfinfo",
        )

        data = response_data.get("data", {}) or {}
        basic_info = data.get("basic_info", {}) or {}
        interactions = data.get("interactions", []) or []

        followers = 0
        following = 0
        for item in interactions:
            if item.get("type") == "fans":
                followers = int(item.get("count", 0))
            elif item.get("type") == "follows":
                following = int(item.get("count", 0))

        return UserResponse(
            user_id=basic_info.get("red_id"),
            nickname=basic_info.get("nickname"),
            avatar=basic_info.get("images"),
            bio=basic_info.get("desc"),
            followers=followers,
            following=following,
        )
