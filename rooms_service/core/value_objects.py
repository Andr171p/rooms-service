from __future__ import annotations

from typing import Any

from collections import UserString
from collections.abc import Callable

from pydantic import BaseModel, Field
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, core_schema

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

    @classmethod
    def __get_pydantic_core_schema__(
            cls,
            source_type: Any,
            handler: Callable[[Any], CoreSchema],
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(str),
        )

    @classmethod
    def __get_pydantic_json_schema__(
            cls,
            core_schema: CoreSchema,
            handler: Callable[[CoreSchema], JsonSchemaValue]
    ) -> JsonSchemaValue:
        json_schema = handler(core_schema)
        json_schema.update({
            "type": "string",
            "pattern": "^[a-zA-Z0-9_]+:[a-zA-Z0-9_]+$",
            "examples": ["message:send", "room:create", "member:delete"]
        })
        return json_schema


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
