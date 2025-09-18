from typing import Self

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

from .constants import (
    HIGHEST_PRIORITY,
    InvitationStatus,
    MemberStatus,
    RoleType,
    RoomType,
    RoomVisibility,
)
from .utils import configure_default_room_settings, current_datetime
from .value_objects import Name, PermissionCode, RoomSettings, Slug


class Room(BaseModel):
    """Комната, абстракция над каналами, группами и чатами.

    Attributes:
        id: Уникальный идентификатор комнаты.
        created_by: Идентификатор пользователя создавшего комнату.
        type: Тип комнаты: channel, group, ...
        avatar_url: URL аватарки комнаты.
        name: Имя комнаты.
        slug: Человеко-читаемый ID для URL.
        visibility: Область видимости комнаты.
        created_at: Дата создания комнаты.
    """
    id: UUID = Field(default_factory=uuid4)
    created_by: UUID
    type: RoomType
    avatar_url: str | None = None
    name: Name | None = None
    slug: Slug | None = None
    visibility: RoomVisibility = RoomVisibility.PUBLIC
    created_at: datetime = Field(default_factory=current_datetime)

    model_config = ConfigDict(from_attributes=True)

    @property
    @computed_field(description="Настройки комнаты")
    def settings(self) -> RoomSettings:
        return configure_default_room_settings(self.type, self.visibility)

    @model_validator(mode="after")
    def validate_name(self) -> Self:
        if self.type == RoomType.DIRECT and self.name is not None:
            raise ValueError("Name of room with direct type must be None!")
        return self


class Member(BaseModel):
    """Участник комнаты.

    Attributes:
        id: Уникальный идентификатор участника.
        user_id: Идентификатор пользователя в системе.
        room_id: Идентификатор комнаты.
        role_id: Роль которая выдана пользователю.
        status: Статус участника.
        joined_at: Дата присоединения пользователя к комнате.
    """
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    room_id: UUID
    role_id: UUID
    status: MemberStatus = MemberStatus.ACTIVE
    joined_at: datetime = Field(default_factory=current_datetime)

    model_config = ConfigDict(from_attributes=True)


class Role(BaseModel):
    """Роль участника внутри комнаты

    Attributes:
        id: Уникальный идентификатор роли.
        type: Тип роли: system, custom ...
        name: Имя роли: owner, admin, ...
        description: Удобно читаемое описание.
        priority: Приоритет роли над другими ролями, где 1 самый высокий приоритет.
    """
    id: UUID = Field(default_factory=uuid4)
    type: RoleType
    name: Name
    description: str | None = None
    priority: int = Field(..., ge=HIGHEST_PRIORITY)


class Permission(BaseModel):
    """Права и привилегии участника.

    Attributes:
        id: Уникальный идентификатор привилегии.
        code: Код привилегии для разработчиков: messages:send, messages:edit, members:delete ...
        category: Ресурс к которому выдаётся привилегия.
    """
    id: UUID = Field(default_factory=uuid4)
    code: PermissionCode
    category: str


class RolePermissions(BaseModel):
    role_id: UUID
    permission_codes: list[PermissionCode]


class MemberPermission(BaseModel):
    """Маппинг ролей и прав"""
    id: UUID = Field(default_factory=uuid4)
    member_id: UUID
    permission_id: UUID
    granted: bool


class Invitation(BaseModel):
    """Приглашение для пользователя на вступление в комнату

    Attributes:
        id: Уникальный идентификатор приглашения.
        room_id: Комната в которую приглашают пользователя.
        inviter_id: Пользователь, который отправил приглашение.
        invitee_id: Пользователь, которого приглашают.
        token: Для генерации уникальной реферальной ссылки.
        status: Статус отправленного приглашения.
        expires_at: Дата истечения приглашения.
        created_at: Дата создания приглашения.
    """
    id: UUID = Field(default_factory=uuid4)
    room_id: UUID
    inviter_id: UUID
    invitee_id: UUID
    token: str
    status: InvitationStatus = InvitationStatus.PENDING
    expires_at: datetime
    created_at: datetime = Field(default_factory=current_datetime)
