"""Integration tests for API response handling and model validation.

Tests that responses from the API are correctly:
- Parsed into Pydantic models
- Validated according to model schemas
- Handled for edge cases (missing fields, extra fields, nested objects)
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from xhs_scraper.client import XHSClient
from xhs_scraper.models import (
    UserResponse,
    NoteResponse,
    CommentResponse,
    SearchResultResponse,
    PaginatedResponse,
)


class TestUserResponseHandling:
    """Test UserResponse model handling from API responses."""

    @pytest.mark.asyncio
    async def test_parse_simple_user_response(self, sample_user_data):
        """API response should parse into UserResponse."""
        user = UserResponse(**sample_user_data)
        assert user.user_id == sample_user_data["user_id"]
        assert user.nickname == sample_user_data["nickname"]

    @pytest.mark.asyncio
    async def test_user_response_with_missing_optional_fields(self):
        """UserResponse should handle missing optional fields."""
        minimal_user = {
            "user_id": "123456",
            "nickname": "TestUser",
        }
        user = UserResponse(**minimal_user)
        assert user.user_id == "123456"
        assert user.nickname == "TestUser"
        assert user.avatar is None

    @pytest.mark.asyncio
    async def test_user_response_ignores_unknown_fields(self, sample_user_data):
        """UserResponse should ignore unknown API fields."""
        data_with_extra = {
            **sample_user_data,
            "unknown_field": "should be ignored",
            "future_api_field": {"nested": "value"},
        }
        user = UserResponse(**data_with_extra)
        assert not hasattr(user, "unknown_field")
        assert not hasattr(user, "future_api_field")

    @pytest.mark.asyncio
    async def test_user_response_with_full_data(self, sample_user_data):
        """UserResponse should handle all available fields."""
        user = UserResponse(**sample_user_data)
        assert user.user_id is not None
        assert user.nickname is not None


class TestNoteResponseHandling:
    """Test NoteResponse model handling from API responses."""

    @pytest.mark.asyncio
    async def test_parse_note_response_with_user(self, sample_note_data):
        """NoteResponse should parse nested user object."""
        note = NoteResponse(**sample_note_data)
        assert note.note_id == sample_note_data["note_id"]
        assert note.title == sample_note_data["title"]

    @pytest.mark.asyncio
    async def test_note_response_with_nested_user_object(self):
        """NoteResponse should handle nested UserResponse."""
        note_data = {
            "note_id": "note123",
            "title": "Test Note",
            "user": {
                "user_id": "user456",
                "nickname": "Author",
            },
        }
        note = NoteResponse(**note_data)
        assert note.note_id == "note123"
        assert isinstance(note.user, UserResponse)
        assert note.user.user_id == "user456"

    @pytest.mark.asyncio
    async def test_note_response_ignores_unknown_fields(self, sample_note_data):
        """NoteResponse should ignore unknown fields."""
        data_with_extra = {
            **sample_note_data,
            "future_field": "unknown",
            "api_timestamp": 1234567890,
        }
        note = NoteResponse(**data_with_extra)
        assert not hasattr(note, "future_field")
        assert not hasattr(note, "api_timestamp")

    @pytest.mark.asyncio
    async def test_note_response_with_stats(self):
        """NoteResponse should handle note statistics."""
        note_data = {
            "note_id": "note123",
            "title": "Test Note",
            "user": {
                "user_id": "user456",
                "nickname": "Author",
            },
            "liked_count": 100,
            "commented_count": 50,
            "shared_count": 25,
        }
        note = NoteResponse(**note_data)
        assert note.liked_count == 100
        assert note.commented_count == 50
        assert note.shared_count == 25


class TestCommentResponseHandling:
    """Test CommentResponse model handling from API responses."""

    @pytest.mark.asyncio
    async def test_parse_comment_response_with_user(self, sample_comment_data):
        """CommentResponse should parse nested user object."""
        comment = CommentResponse(**sample_comment_data)
        assert comment.comment_id == sample_comment_data["comment_id"]
        assert comment.content == sample_comment_data["content"]

    @pytest.mark.asyncio
    async def test_comment_response_with_nested_user(self):
        """CommentResponse should create UserResponse from nested data."""
        comment_data = {
            "comment_id": "c123",
            "content": "Great note!",
            "user": {
                "user_id": "user789",
                "nickname": "Commenter",
            },
        }
        comment = CommentResponse(**comment_data)
        assert isinstance(comment.user, UserResponse)
        assert comment.user.nickname == "Commenter"

    @pytest.mark.asyncio
    async def test_comment_response_with_sub_comments(self):
        """CommentResponse should handle sub-comments list."""
        comment_data = {
            "comment_id": "c123",
            "content": "Main comment",
            "user": {
                "user_id": "user789",
                "nickname": "Commenter",
            },
            "sub_comments": [
                {
                    "comment_id": "c124",
                    "content": "Reply 1",
                    "user": {
                        "user_id": "user790",
                        "nickname": "Replier",
                    },
                },
            ],
        }
        comment = CommentResponse(**comment_data)
        assert len(comment.sub_comments) == 1
        assert comment.sub_comments[0].content == "Reply 1"

    @pytest.mark.asyncio
    async def test_comment_response_ignores_unknown_fields(self, sample_comment_data):
        """CommentResponse should ignore unknown fields."""
        data_with_extra = {
            **sample_comment_data,
            "metadata": {"created_at": "2024-01-01"},
            "rank": 5,
        }
        comment = CommentResponse(**data_with_extra)
        assert not hasattr(comment, "metadata")
        assert not hasattr(comment, "rank")


class TestSearchResultResponseHandling:
    """Test SearchResultResponse model handling from API responses."""

    @pytest.mark.asyncio
    async def test_parse_search_result_response(self, sample_search_result):
        """SearchResultResponse should parse search API response."""
        result = SearchResultResponse(**sample_search_result)
        assert len(result.items) == len(sample_search_result["items"])
        assert result.cursor == sample_search_result["cursor"]
        assert result.has_more == sample_search_result["has_more"]

    @pytest.mark.asyncio
    async def test_search_result_response_with_minimal_data(self):
        """SearchResultResponse should handle minimal data."""
        minimal_result = {
            "note_id": "note999",
            "title": "Search Result",
        }
        result = SearchResultResponse(**minimal_result)
        assert result.note_id == "note999"
        assert result.title == "Search Result"

    @pytest.mark.asyncio
    async def test_search_result_response_ignores_unknown_fields(
        self, sample_search_result
    ):
        """SearchResultResponse should ignore unknown fields."""
        data_with_extra = {
            **sample_search_result,
            "rank_score": 0.95,
            "search_metadata": {"query": "test"},
        }
        result = SearchResultResponse(**data_with_extra)
        assert not hasattr(result, "rank_score")
        assert not hasattr(result, "search_metadata")


class TestPaginatedResponseHandling:
    """Test PaginatedResponse model handling from API responses."""

    @pytest.mark.asyncio
    async def test_parse_paginated_response_with_notes(self):
        """PaginatedResponse should handle paginated note results."""
        response_data = {
            "items": [
                {
                    "note_id": "note1",
                    "title": "Note 1",
                    "user": {"user_id": "user1", "nickname": "User1"},
                },
                {
                    "note_id": "note2",
                    "title": "Note 2",
                    "user": {"user_id": "user2", "nickname": "User2"},
                },
            ],
            "cursor": "next_page_cursor",
            "has_more": True,
        }
        paginated = PaginatedResponse(**response_data)
        assert len(paginated.items) == 2
        assert paginated.cursor == "next_page_cursor"
        assert paginated.has_more is True

    @pytest.mark.asyncio
    async def test_parse_paginated_response_with_users(self):
        """PaginatedResponse should handle paginated user results."""
        response_data = {
            "items": [
                {"user_id": "u1", "nickname": "User1"},
                {"user_id": "u2", "nickname": "User2"},
            ],
            "cursor": "cursor123",
            "has_more": False,
        }
        paginated = PaginatedResponse(**response_data)
        assert len(paginated.items) == 2
        assert paginated.has_more is False

    @pytest.mark.asyncio
    async def test_paginated_response_empty_items(self):
        """PaginatedResponse should handle empty items list."""
        response_data = {
            "items": [],
            "cursor": None,
            "has_more": False,
        }
        paginated = PaginatedResponse(**response_data)
        assert len(paginated.items) == 0
        assert paginated.has_more is False

    @pytest.mark.asyncio
    async def test_paginated_response_ignores_unknown_fields(self):
        """PaginatedResponse should ignore unknown fields."""
        response_data = {
            "items": [{"user_id": "u1", "nickname": "User1"}],
            "cursor": "cursor123",
            "has_more": False,
            "total_count": 100,
            "page_size": 20,
        }
        paginated = PaginatedResponse(**response_data)
        assert not hasattr(paginated, "total_count")
        assert not hasattr(paginated, "page_size")

    @pytest.mark.asyncio
    async def test_paginated_response_with_optional_cursor(self):
        """PaginatedResponse should handle optional cursor."""
        response_data = {
            "items": [{"user_id": "u1", "nickname": "User1"}],
            "cursor": None,
            "has_more": False,
        }
        paginated = PaginatedResponse(**response_data)
        assert paginated.cursor is None


class TestClientWithMockedResponses:
    """Test XHSClient with mocked API responses."""

    @pytest.mark.asyncio
    async def test_client_parses_user_response(self):
        """Client should parse user API response into model."""
        client = XHSClient(cookies={"a1": "test_a1_value"})

        mock_response = {
            "user_id": "user123",
            "nickname": "TestUser",
            "avatar": "https://example.com/avatar.jpg",
        }

        async with client:
            with patch.object(
                client._http, "request", new_callable=AsyncMock
            ) as mock_req:
                mock_req.return_value = AsyncMock(
                    status_code=200,
                    json=MagicMock(return_value=mock_response),
                )

                result = await client._request("GET", "/api/user")

                user = UserResponse(**result)
                assert user.user_id == "user123"
                assert user.nickname == "TestUser"

    @pytest.mark.asyncio
    async def test_client_parses_note_response(self):
        """Client should parse note API response into model."""
        client = XHSClient(cookies={"a1": "test_a1_value"})

        mock_response = {
            "note_id": "note123",
            "title": "Test Note",
            "user": {
                "user_id": "user456",
                "nickname": "Author",
            },
            "liked_count": 42,
        }

        async with client:
            with patch.object(
                client._http, "request", new_callable=AsyncMock
            ) as mock_req:
                mock_req.return_value = AsyncMock(
                    status_code=200,
                    json=MagicMock(return_value=mock_response),
                )

                result = await client._request("POST", "/api/note")

                note = NoteResponse(**result)
                assert note.note_id == "note123"
                assert note.user.user_id == "user456"

    @pytest.mark.asyncio
    async def test_client_parses_paginated_response(self):
        """Client should parse paginated API response."""
        client = XHSClient(cookies={"a1": "test_a1_value"})

        mock_response = {
            "items": [
                {
                    "note_id": "n1",
                    "title": "Note 1",
                    "user": {"user_id": "u1", "nickname": "User1"},
                },
                {
                    "note_id": "n2",
                    "title": "Note 2",
                    "user": {"user_id": "u2", "nickname": "User2"},
                },
            ],
            "cursor": "next_cursor",
            "has_more": True,
        }

        async with client:
            with patch.object(
                client._http, "request", new_callable=AsyncMock
            ) as mock_req:
                mock_req.return_value = AsyncMock(
                    status_code=200,
                    json=MagicMock(return_value=mock_response),
                )

                result = await client._request("GET", "/api/search")

                paginated = PaginatedResponse(**result)
                assert len(paginated.items) == 2
                assert paginated.has_more is True

    @pytest.mark.asyncio
    async def test_client_response_with_extra_api_fields(self):
        """Client should ignore extra fields in API response."""
        client = XHSClient(cookies={"a1": "test_a1_value"})

        mock_response = {
            "user_id": "user123",
            "nickname": "TestUser",
            "future_feature": "should be ignored",
            "api_version": "v2",
        }

        async with client:
            with patch.object(
                client._http, "request", new_callable=AsyncMock
            ) as mock_req:
                mock_req.return_value = AsyncMock(
                    status_code=200,
                    json=MagicMock(return_value=mock_response),
                )

                result = await client._request("GET", "/api/user")

                user = UserResponse(**result)
                assert user.user_id == "user123"
                assert not hasattr(user, "future_feature")


class TestResponseValidationEdgeCases:
    """Test edge cases in response validation."""

    @pytest.mark.asyncio
    async def test_user_response_with_empty_nickname(self):
        """UserResponse should accept empty nickname."""
        user_data = {
            "user_id": "user123",
            "nickname": "",
        }
        user = UserResponse(**user_data)
        assert user.nickname == ""

    @pytest.mark.asyncio
    async def test_note_response_with_zero_stats(self):
        """NoteResponse should handle zero engagement stats."""
        note_data = {
            "note_id": "note123",
            "title": "Unpopular Note",
            "user": {"user_id": "u1", "nickname": "Author"},
            "liked_count": 0,
            "commented_count": 0,
            "shared_count": 0,
        }
        note = NoteResponse(**note_data)
        assert note.liked_count == 0
        assert note.commented_count == 0

    @pytest.mark.asyncio
    async def test_comment_response_with_empty_sub_comments(self):
        """CommentResponse should handle empty sub-comments list."""
        comment_data = {
            "comment_id": "c123",
            "content": "Comment",
            "user": {"user_id": "u1", "nickname": "User"},
            "sub_comments": [],
        }
        comment = CommentResponse(**comment_data)
        assert len(comment.sub_comments) == 0

    @pytest.mark.asyncio
    async def test_paginated_response_with_none_cursor(self):
        """PaginatedResponse should accept None cursor."""
        response_data = {
            "items": [{"user_id": "u1", "nickname": "User1"}],
            "cursor": None,
            "has_more": False,
        }
        paginated = PaginatedResponse(**response_data)
        assert paginated.cursor is None
        assert paginated.has_more is False


class TestResponseModelConsistency:
    """Test consistency of response model conversions."""

    @pytest.mark.asyncio
    async def test_convert_user_data_to_model_multiple_times(self, sample_user_data):
        """Multiple conversions of same data should produce equivalent models."""
        user1 = UserResponse(**sample_user_data)
        user2 = UserResponse(**sample_user_data)

        assert user1.user_id == user2.user_id
        assert user1.nickname == user2.nickname

    @pytest.mark.asyncio
    async def test_nested_model_consistency(self):
        """Nested models should be consistent across conversions."""
        note_data1 = {
            "note_id": "n1",
            "title": "Note",
            "user": {"user_id": "u1", "nickname": "User1"},
        }
        note_data2 = {
            "note_id": "n1",
            "title": "Note",
            "user": {"user_id": "u1", "nickname": "User1"},
        }

        note1 = NoteResponse(**note_data1)
        note2 = NoteResponse(**note_data2)

        assert note1.user.user_id == note2.user.user_id
        assert note1.user.nickname == note2.user.nickname
