"""Все модели настроек в этом модуле должны иметь значения по умолчанию"""

from uuid import UUID

from pydantic import BaseModel, Field

from .constants import (
    ALL_ALLOWED_MEDIA_FORMATS,
    DEFAULT_PINNED_MESSAGES,
    MAX_MEMBERS,
    MAX_PINNED_MESSAGES,
    MIN_MEMBERS,
    MIN_PINNED_MESSAGES,
)
from .enums import JoinPermission, MediaType, RoomVisibility
from .utils import all_media_types


class MessageProperties(BaseModel):
    """Настройки сообщений внутри комнаты"""
    allow_forwarding: bool = True
    history_visible_for_new_members: bool = False
    pinned_limit: int = Field(
        default=DEFAULT_PINNED_MESSAGES,
        ge=MIN_PINNED_MESSAGES,
        le=MAX_PINNED_MESSAGES
    )
    profanity_filter: bool = False
    badwords: set[str] = Field(default_factory=set)


class MediaProperties(BaseModel):
    """Настройки медиа внутри комнаты"""
    allowed_types: list[MediaType] = Field(default_factory=all_media_types)
    allowed_formats: list[str] = Field(default_factory=lambda: ALL_ALLOWED_MEDIA_FORMATS)


class PrivacyProperties(BaseModel):
    """Настройки приватности"""
    join_permission: JoinPermission = JoinPermission.OPEN


class RoomProperties(BaseModel):
    """Настройки комнаты"""
    room_id: UUID
    visibility: RoomVisibility = RoomVisibility.PUBLIC
    max_members: int = Field(default=..., ge=MIN_MEMBERS, le=MAX_MEMBERS)
    messages: MessageProperties = Field(default_factory=MessageProperties)
    media: MediaProperties = Field(default_factory=MediaProperties)
    privacy: PrivacyProperties = Field(default_factory=PrivacyProperties)
