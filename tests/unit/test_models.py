"""Unit tests for xhs_scraper.models module."""

import pytest
from typing import Dict, Any, List, Optional
from xhs_scraper.models import (
    UserResponse,
    CommentResponse,
    NoteResponse,
    SearchResultResponse,
    PaginatedResponse,
)


class TestUserResponse:
    """Test UserResponse Pydantic model."""

    def test_user_response_valid_data(self):
        """Create UserResponse with valid data."""
        user = UserResponse(
            user_id="123456",
            nickname="testuser",
            avatar="https://example.com/avatar.jpg",
            bio="Test bio",
            followers=100,
            following=50,
        )
        assert user.user_id == "123456"
        assert user.nickname == "testuser"
        assert user.followers == 100
        assert user.following == 50

    def test_user_response_optional_fields(self):
        """Create UserResponse with only user_id."""
        user = UserResponse(user_id="123")
        assert user.user_id == "123"
        assert user.nickname is None
        assert user.avatar is None

    def test_user_response_all_optional(self):
        """Create UserResponse with no required fields."""
        user = UserResponse()
        assert user.user_id is None
        assert user.nickname is None

    def test_user_response_ignores_extra_fields(self):
        """UserResponse should ignore extra fields (extra='ignore')."""
        user = UserResponse(
            user_id="123",
            nickname="test",
            unknown_field="should_be_ignored",
            extra_data={"nested": "value"},
        )
        assert user.user_id == "123"
        assert user.nickname == "test"
        assert not hasattr(user, "unknown_field")
        assert not hasattr(user, "extra_data")


class TestCommentResponse:
    """Test CommentResponse Pydantic model."""

    def test_comment_response_valid_data(self):
        """Create CommentResponse with valid data."""
        comment = CommentResponse(
            comment_id="c123",
            content="Test comment",
            user=UserResponse(user_id="u123", nickname="commenter"),
            create_time=1672531200,
        )
        assert comment.comment_id == "c123"
        assert comment.content == "Test comment"
        assert comment.user.user_id == "u123"
        assert comment.create_time == 1672531200

    def test_comment_response_nested_user(self):
        """Create CommentResponse with nested UserResponse."""
        user_data = {"user_id": "u456", "nickname": "nested_user"}
        comment = CommentResponse(comment_id="c456", user=user_data)
        assert comment.user.user_id == "u456"
        assert comment.user.nickname == "nested_user"

    def test_comment_response_with_sub_comments(self):
        """Create CommentResponse with nested sub_comments."""
        sub_comment = {"comment_id": "sub1", "content": "Reply"}
        comment = CommentResponse(
            comment_id="c789",
            content="Main comment",
            sub_comments=[sub_comment],
        )
        assert comment.comment_id == "c789"
        assert len(comment.sub_comments) == 1
        assert comment.sub_comments[0].comment_id == "sub1"

    def test_comment_response_ignores_extra_fields(self):
        """CommentResponse should ignore extra fields."""
        comment = CommentResponse(
            comment_id="c123",
            unexpected_field="ignored",
            extra_data=123,
        )
        assert comment.comment_id == "c123"
        assert not hasattr(comment, "unexpected_field")


class TestNoteResponse:
    """Test NoteResponse Pydantic model."""

    def test_note_response_valid_data(self):
        """Create NoteResponse with valid data."""
        note = NoteResponse(
            note_id="n123",
            title="Test Note",
            desc="Test description",
            images=["img1.jpg", "img2.jpg"],
            video="video.mp4",
            stats={"likes": 100, "comments": 10},
        )
        assert note.note_id == "n123"
        assert note.title == "Test Note"
        assert len(note.images) == 2
        assert note.video == "video.mp4"
        assert note.stats["likes"] == 100

    def test_note_response_minimal_data(self):
        """Create NoteResponse with minimal data."""
        note = NoteResponse(note_id="n456")
        assert note.note_id == "n456"
        assert note.title is None
        assert note.images is None

    def test_note_response_with_user(self):
        """Create NoteResponse with nested UserResponse."""
        user_data = {"user_id": "u789", "nickname": "author"}
        note = NoteResponse(note_id="n789", title="Article", user=user_data)
        assert note.user.user_id == "u789"
        assert note.user.nickname == "author"

    def test_note_response_stats_with_any_dict(self):
        """Stats field accepts any dictionary structure."""
        stats = {
            "likes": 1000,
            "comments": 50,
            "shares": 25,
            "custom_metric": "value",
        }
        note = NoteResponse(note_id="n999", stats=stats)
        assert note.stats == stats
        assert note.stats["custom_metric"] == "value"

    def test_note_response_ignores_extra_fields(self):
        """NoteResponse should ignore extra fields."""
        note = NoteResponse(
            note_id="n123",
            title="Test",
            unwanted_field="ignored",
        )
        assert note.note_id == "n123"
        assert not hasattr(note, "unwanted_field")


class TestSearchResultResponse:
    """Test SearchResultResponse Pydantic model."""

    def test_search_result_response_valid(self):
        """Create SearchResultResponse with valid data."""
        items = [
            {"note_id": "n1", "title": "Note 1"},
            {"note_id": "n2", "title": "Note 2"},
        ]
        result = SearchResultResponse(
            items=items,
            has_more=True,
            cursor="next_cursor_token",
        )
        assert len(result.items) == 2
        assert result.items[0].note_id == "n1"
        assert result.has_more is True
        assert result.cursor == "next_cursor_token"

    def test_search_result_response_empty(self):
        """Create SearchResultResponse with no items."""
        result = SearchResultResponse()
        assert result.items is None
        assert result.has_more is False
        assert result.cursor is None

    def test_search_result_response_defaults(self):
        """SearchResultResponse has_more defaults to False."""
        result = SearchResultResponse(items=[])
        assert result.has_more is False


class TestPaginatedResponse:
    """Test generic PaginatedResponse model."""

    def test_paginated_response_with_notes(self):
        """Create PaginatedResponse[NoteResponse]."""
        items = [
            {"note_id": "n1", "title": "Note 1"},
            {"note_id": "n2", "title": "Note 2"},
        ]
        paginated: PaginatedResponse[NoteResponse] = PaginatedResponse(
            items=items,
            cursor="token123",
            has_more=True,
        )
        assert len(paginated.items) == 2
        assert paginated.items[0]["note_id"] == "n1"
        assert paginated.cursor == "token123"
        assert paginated.has_more is True

    def test_paginated_response_with_users(self):
        """Create PaginatedResponse[UserResponse]."""
        items = [
            {"user_id": "u1", "nickname": "user1"},
            {"user_id": "u2", "nickname": "user2"},
        ]
        paginated: PaginatedResponse[UserResponse] = PaginatedResponse(
            items=items,
            has_more=False,
        )
        assert len(paginated.items) == 2
        assert paginated.items[0]["user_id"] == "u1"
        assert paginated.has_more is False

    def test_paginated_response_empty(self):
        """Create empty PaginatedResponse."""
        paginated: PaginatedResponse[NoteResponse] = PaginatedResponse()
        assert paginated.items is None
        assert paginated.has_more is False
        assert paginated.cursor is None

    def test_paginated_response_ignores_extra(self):
        """PaginatedResponse ignores extra fields."""
        paginated: PaginatedResponse[UserResponse] = PaginatedResponse(
            items=[],
            extra_field="ignored",
            metadata={"nested": "also_ignored"},
        )
        assert paginated.items == []
        assert not hasattr(paginated, "extra_field")


class TestModelIntegration:
    """Test integration between models."""

    def test_nested_model_hierarchy(self):
        """Test creating complex nested model structure."""
        data = {
            "note_id": "n123",
            "title": "Integrated Note",
            "user": {
                "user_id": "u123",
                "nickname": "author",
                "followers": 1000,
            },
        }
        note = NoteResponse(**data)
        assert note.note_id == "n123"
        assert note.user.user_id == "u123"
        assert note.user.followers == 1000

    def test_comment_with_user_and_sub_comments(self):
        """Test CommentResponse with nested user and sub-comments."""
        data = {
            "comment_id": "c1",
            "content": "Main comment",
            "user": {"user_id": "u1", "nickname": "user1"},
            "sub_comments": [
                {
                    "comment_id": "c1_1",
                    "content": "Reply 1",
                    "user": {"user_id": "u2", "nickname": "user2"},
                }
            ],
        }
        comment = CommentResponse(**data)
        assert comment.comment_id == "c1"
        assert comment.user.nickname == "user1"
        assert comment.sub_comments[0].user.nickname == "user2"
