from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from ..constants import (
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
    UNLIMITED_MEDIA_FORMATS,
)
from .enums import JoinPermission, MediaType, RoleType
from .primitives import Name, PermissionCode, RolePriority


class Role(BaseModel):
    """Сущность роли (для разграничения прав и доступа к контенту внутри комнаты)

    Attributes:
        type: Тип роли: system, custom ...
        name: Имя роли: owner, admin, ...
        priority: Приоритет роли над другими ролями, где 100 самый высокий приоритет.
        permissions: Права которые принадлежат роли.
    """
    type: RoleType
    name: Name
    priority: RolePriority
    permissions: list[Permission]


class Permission(BaseModel):
    """Права и привилегии участника.

    Attributes:
        code: Код привилегии для разработчиков: message:send, message:edit, member:delete ...
        category: Ресурс к которому выдаётся привилегия.
    """
    code: PermissionCode
    category: str

    def __hash__(self) -> int:
        return hash(self.code)

    def __eq__(self, other: Permission) -> bool:
        if not isinstance(other, Permission):
            return False
        return self.code == other.code and self.category == other.category


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
    max_members: int = Field(default=MAX_MEMBERS, ge=MIN_MEMBERS, le=MAX_MEMBERS)
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
