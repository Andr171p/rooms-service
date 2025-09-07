from __future__ import annotations

from collections import UserString

from pydantic import BaseModel, Field

from .constants import (
    DEFAULT_ADMINS,
    DEFAULT_MEDIA_SIZE,
    DEFAULT_PINNED_MESSAGES,
    MAX_ADMINS,
    MAX_MEDIA_SIZE,
    MAX_MEMBERS,
    MAX_PINNED_MESSAGES,
    MIN_ADMINS,
    MIN_MEDIA_SIZE,
    MIN_MEMBERS,
    MIN_PINNED_MESSAGES,
    PERMISSION_CODE_PARTS,
    UNLIMITED_MEDIA_FORMATS,
    JoinPermission,
    MediaType,
)


class PermissionCode(UserString):
    """Строка для валидации кода привилегий."""
    def __init__(self, seq: str):
        super().__init__(seq)
        self.data = self.validate(self.data)

    @classmethod
    def validate(cls, code: str) -> str:
        if ":" not in code:
            raise ValueError(
                """Permission code must contains ':'!
                For example: 'message:send', 'room:create', 'member:delete
                """
            )
        if len(code.split(":")) != PERMISSION_CODE_PARTS:
            raise ValueError("Invalid permission code!")
        return code


class RoomSettings(BaseModel):
    """Настройки комнаты, настраиваемые разделы:
     - участники
     - сообщения
     - медиа
    """
    members: RoomMembersSettings
    messages: RoomMessagesSettings
    media: RoomMediaSettings


class RoomMessagesSettings(BaseModel):
    allow_forwarding: bool = True
    history_visibility_for_new_members: bool = True
    pinned_limit: int = Field(
        default=DEFAULT_PINNED_MESSAGES,
        ge=MIN_PINNED_MESSAGES,
        le=MAX_PINNED_MESSAGES
    )
    profanity_filter: bool = False
    forbidden_words: list[str] = Field(default_factory=list)


class RoomMembersSettings(BaseModel):
    max_members: int = Field(ge=MIN_MEMBERS, le=MAX_MEMBERS)
    max_admins: int = Field(default=DEFAULT_ADMINS, ge=MIN_ADMINS, le=MAX_ADMINS)
    join_permission: JoinPermission = JoinPermission.OPEN


class RoomMediaSettings(BaseModel):
    allow_media: bool = True
    max_size: int = Field(default=DEFAULT_MEDIA_SIZE, ge=MIN_MEDIA_SIZE, le=MAX_MEDIA_SIZE)
    allowed_types: list[str] = Field(default=list(MediaType))
    allowed_formats: list[str] = Field(default=UNLIMITED_MEDIA_FORMATS)
