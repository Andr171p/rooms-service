from __future__ import annotations

from typing import Annotated, Any

from collections import UserString
from collections.abc import Callable
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field
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
)

# Уникальный UUID идентификатор
Id = Annotated[UUID, Field(default_factory=uuid4)]


class EventStatus(StrEnum):
    """Статусы жизненного цикла события"""
    NEW = "new"
    PENDING = "pending"
    DONE = "done"
    FAILED = "failed"


class RoomType(StrEnum):
    """Тип комнаты (чата)"""
    DIRECT = "direct"  # Личный чат one to one
    GROUP = "group"  # Групповой чат
    CHANNEL = "channel"  # Канал: новости, блог и.т.д


class RoomVisibility(StrEnum):
    """Видимость комнаты для других пользователей"""
    PRIVATE = "private"
    PUBLIC = "public"
    DELETED = "deleted"
    BANNED = "banned"


class MemberStatus(StrEnum):
    """Статус участника"""
    ACTIVE = "active"  # Может полноценно использовать разрешённый ему функционал
    MUTED = "muted"  # Не может писать и взаимодействовать с сообщениями
    BANNED = "banned"  # Не может ни взаимодействовать, ни читать контент


class SystemRole(StrEnum):
    """Системные роли участника комнаты"""
    OWNER = "owner"          # Владелец комнаты, самые высокие привилегии
    ADMIN = "admin"          # Администратор, может управлять участниками + привилегии модератора
    MODERATOR = "moderator"  # Модератор, может удалять и управлять сообщениями
    MEMBER = "member"        # Участник, может взаимодействовать с сообщениями
    GUEST = "guest"          # Гость
    READER = "reader"        # Читатель, может только просматривать сообщения
    BOT = "bot"              # Бот


class RoleType(StrEnum):
    """Тип роли участника"""
    SYSTEM = "system"  # Системная роль, не подлежит изменениям
    CUSTOM = "custom"  # Роль, которую может создать пользователь


class MediaType(StrEnum):
    """Возможные типы медиа контента"""
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    AUDIO = "audio"
    STICKER = "sticker"


class JoinPermission(StrEnum):
    """Правила присоединения новых участников"""
    OPEN = "open"
    APPROVAL = "approval"
    INVITE_ONLY = "invite_only"


class InvitationStatus(StrEnum):
    """Статус отправленного приглашения в комнату"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class MemberPermissionStatus(StrEnum):
    """Статус права для участника"""
    GRANT = "grant"
    DENY = "deny"


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


class RolePriority(_IntPrimitiveValidator):
    """Тип для валидации приоритета роли"""
    @classmethod
    def validate(cls, value: int, *args, **kwargs) -> int:  # noqa: ARG003
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


class MemberIdentity(BaseModel):
    room_id: UUID
    user_id: UUID

    model_config = ConfigDict(frozen=True)
