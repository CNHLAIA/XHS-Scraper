"""Pydantic response models for XHS scraper."""

from typing import Generic, List, Optional, TypeVar, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class UserResponse(BaseModel):
    """User information model."""

    model_config = ConfigDict(extra="ignore")

    user_id: Optional[str] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None
    followers: Optional[int] = None
    following: Optional[int] = None


class CommentResponse(BaseModel):
    """Comment model."""

    model_config = ConfigDict(extra="ignore")

    comment_id: Optional[str] = None
    content: Optional[str] = None
    user: Optional[UserResponse] = None
    create_time: Optional[int] = None
    sub_comments: Optional[List["CommentResponse"]] = None


CommentResponse.model_rebuild()


class NoteResponse(BaseModel):
    """Note/Post response model."""

    model_config = ConfigDict(extra="ignore")

    note_id: Optional[str] = None
    title: Optional[str] = None
    desc: Optional[str] = None
    images: Optional[List[str]] = None
    video: Optional[str] = None
    user: Optional[UserResponse] = None
    stats: Optional[Dict[str, Any]] = None
    liked_count: Optional[int] = None
    commented_count: Optional[int] = None
    shared_count: Optional[int] = None


class SearchResultResponse(NoteResponse):
    """Search result response model - extends NoteResponse with search-specific fields."""

    model_config = ConfigDict(extra="ignore")

    items: Optional[List[NoteResponse]] = None
    has_more: Optional[bool] = False
    cursor: Optional[str] = None


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response model."""

    model_config = ConfigDict(extra="ignore")

    items: Optional[List[T]] = None
    cursor: Optional[str] = None
    has_more: Optional[bool] = False
