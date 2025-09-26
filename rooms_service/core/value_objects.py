from __future__ import annotations

from typing import Any

from collections import UserString
from collections.abc import Callable

from pydantic import BaseModel, Field
from pydantic_core import CoreSchema, core_schema

from .constants import (
    DEFAULT_ADMINS,
    DEFAULT_MEDIA_SIZE,
    DEFAULT_PINNED_MESSAGES,
    MAX_ADMINS,
    MAX_MEDIA_SIZE,
    MAX_MEMBERS,
    MAX_NAME_LENGTH,
    MAX_PINNED_MESSAGES,
    MAX_ROLE_PRIORITY,
    MIN_ADMINS,
    MIN_MEDIA_SIZE,
    MIN_MEMBERS,
    MIN_NAME_LENGTH,
    MIN_PERMISSION_CODE_PARTS,
    MIN_PINNED_MESSAGES,
    MIN_ROLE_PRIORITY,
    UNLIMITED_MEDIA_FORMATS,
    JoinPermission,
    MediaType,
)

MessagePayload = str | dict[str, Any] | BaseModel | list[BaseModel] | list[dict[str, Any]]


class _IntPrimitiveValidator(int):
    def __new__(cls, value: int, *args, **kwargs) -> int:
        value = cls.validate(value, *args, **kwargs)
        return super().__new__(cls, value)

    @classmethod
    def validate(cls, value: int, *args, **kwargs) -> int: pass

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


class PriorityInt(_IntPrimitiveValidator):
    """Тип для валидации приоритета роли"""
    @classmethod
    def validate(cls, value: int, *args, **kwargs) -> int:
        if not (MIN_ROLE_PRIORITY <= value <= MAX_ROLE_PRIORITY):
            raise ValueError(
                f"Priority must be between {MIN_ROLE_PRIORITY} and {MAX_ROLE_PRIORITY}!"
            )
        return value


class _StrPrimitiveValidator(UserString):
    def __init__(self, seq: str) -> None:
        super().__init__(seq)
        self.data = self.validate(self.data)

    @classmethod
    def validate(cls, value: str) -> str: pass

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


class PermissionCode(_StrPrimitiveValidator):
    """Строка для валидации кода привилегий."""

    @classmethod
    def validate(cls, code: str) -> str:
        if ":" not in code:
            raise ValueError(
                """Permission code must contains ':'!
                For example: 'message:send', 'room:create', 'member:delete
                """
            )
        if len(code.split(":")) < MIN_PERMISSION_CODE_PARTS:
            raise ValueError("Invalid permission code!")
        return code


class Name(_StrPrimitiveValidator):
    """Строка для валидации имени сущности"""

    @classmethod
    def validate(cls, name: str) -> str:
        if not (MIN_NAME_LENGTH <= len(name) <= MAX_NAME_LENGTH):
            raise ValueError("Name length must be between 1 and 100 characters!")
        return name


class Slug(_StrPrimitiveValidator):
    """Строка для валидации псевдонима сущности"""

    @classmethod
    def validate(cls, slug: str) -> str:
        if not (MIN_NAME_LENGTH <= len(slug) <= MAX_NAME_LENGTH):
            raise ValueError("Name length must be between 1 and 100 characters!")
        return slug.lower()


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
