from __future__ import annotations

from typing import Self

from abc import ABC
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

from .rules import configure_default_room_settings, current_datetime
from .value_objects import (
    Id,
    MemberStatus,
    Name,
    PermissionCode,
    RolePriority,
    RoleType,
    RoomSettings,
    RoomType,
    RoomVisibility,
    Slug,
)


class _Entity(BaseModel, ABC):
    id: Id

    model_config = ConfigDict(from_attributes=True)


class Room(_Entity):
    """Комната, абстракция над каналами, группами и чатами.

    Attributes:
        created_by: Идентификатор пользователя создавшего комнату.
        type: Тип комнаты: channel, group, ...
        avatar_url: URL аватарки комнаты.
        name: Имя комнаты.
        slug: Человеко-читаемый ID для URL.
        visibility: Область видимости комнаты.
        created_at: Дата создания комнаты.
    """
    created_by: UUID
    type: RoomType
    avatar_url: str | None = None
    name: Name | None = None
    slug: Slug | None = None
    visibility: RoomVisibility = RoomVisibility.PUBLIC
    created_at: datetime = Field(default_factory=current_datetime)

    @property
    @computed_field(description="Настройки комнаты")
    def settings(self) -> RoomSettings:
        return configure_default_room_settings(self.type, self.visibility)

    @model_validator(mode="after")
    def validate_name(self) -> Self:
        if self.type == RoomType.DIRECT and self.name is not None:
            raise ValueError("Name of room with direct type must be None!")
        return self


class Member(_Entity):
    """Участник комнаты.

    Attributes:
        id: Уникальный идентификатор участника.
        user_id: Идентификатор пользователя в системе.
        room_id: Идентификатор комнаты.
        role: Роль которая выдана пользователю.
        status: Статус участника.
        joined_at: Дата присоединения пользователя к комнате.
    """
    user_id: UUID
    room_id: UUID
    role: Role
    status: MemberStatus = MemberStatus.ACTIVE
    joined_at: datetime = Field(default_factory=current_datetime)


class Role(_Entity):
    """Сущность роли (для разграничения прав и доступа к контенту внутри комнаты)

    Attributes:
        type: Тип роли: system, custom ...
        name: Имя роли: owner, admin, ...
        description: Человеко-читаемое описание.
        priority: Приоритет роли над другими ролями, где 100 самый высокий приоритет.
    """
    type: RoleType
    name: Name
    description: str
    priority: RolePriority


class Permission(_Entity):
    """Права и привилегии участника.

    Attributes:
        code: Код привилегии для разработчиков: messages:send, messages:edit, members:delete ...
        category: Ресурс к которому выдаётся привилегия.
    """
    code: PermissionCode
    category: str
