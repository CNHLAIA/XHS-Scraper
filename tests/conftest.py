"""Shared pytest fixtures for unit and integration tests."""

import pytest
from unittest.mock import MagicMock, AsyncMock


@pytest.fixture
def mock_xhshow_client():
    """Provide a mocked Xhshow client for signature tests."""
    client = MagicMock()
    client.sign_get = MagicMock(
        return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
    )
    client.sign_post = MagicMock(
        return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
    )
    return client


@pytest.fixture
def mock_session_manager():
    """Provide a mocked SessionManager."""
    manager = MagicMock()
    manager.cookies = {"cookie1": "value1"}
    return manager


@pytest.fixture
def mock_signature_provider():
    """Provide a mocked SignatureProvider for error handling tests."""
    provider = MagicMock()
    provider.sign_get = MagicMock(
        return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
    )
    provider.sign_post = MagicMock(
        return_value={"x-s": "signature_value", "x-t": "timestamp_value"}
    )
    return provider


@pytest.fixture
def sample_user_data():
    """Provide sample user response data."""
    return {
        "user_id": "test_user_123",
        "nickname": "TestUser",
        "avatar": "https://example.com/avatar.jpg",
        "description": "Test user description",
    }


@pytest.fixture
def sample_note_data():
    """Provide sample note response data."""
    return {
        "note_id": "test_note_123",
        "title": "Test Note Title",
        "desc": "Test note description",
        "type": "text",
        "user": {"user_id": "test_user_123", "nickname": "TestUser"},
        "stats": {"view_count": 100, "like_count": 10, "comment_count": 5},
    }


@pytest.fixture
def sample_comment_data():
    """Provide sample comment response data."""
    return {
        "comment_id": "test_comment_123",
        "content": "Test comment",
        "user": {"user_id": "test_user_123", "nickname": "TestUser"},
        "create_time": 1234567890,
        "sub_comments": [],
    }


@pytest.fixture
def sample_search_result():
    """Provide sample search result data."""
    return {
        "items": [
            {"note_id": "note_1", "title": "Note 1"},
            {"note_id": "note_2", "title": "Note 2"},
        ],
        "cursor": "next_page_token",
        "has_more": True,
    }
