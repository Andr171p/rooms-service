from typing import Self

from abc import ABC
from collections.abc import Iterator
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt

from .commands import CreateRoomCommand
from .entities import Permission, Role
from .events import Event, EventT, PayloadT, RoomCreated
from .rules import (
    GUEST_PERMISSIONS,
    MEMBER_PERMISSIONS,
    OWNER_PERMISSIONS,
    configure_default_room_settings,
)
from .value_objects import (
    CurrentDatetime,
    EventStatus,
    EventType,
    Id,
    Name,
    PermissionCode,
    RoomSettings,
    RoomType,
    RoomVisibility,
    Slug,
)


class AggregateRoot(BaseModel, ABC):
    id: Id
    _events: list[EventT] = Field(default_factory=list, exclude=True)
    _version: str = Field(default="0.1.0", exclude=True)

    model_config = ConfigDict(
        arbitrary_types_allowed=True, validate_assignment=True, frozen=False
    )

    def _register_event(self, type: EventType, payload: PayloadT) -> None:  # noqa: A002
        self._events.append(Event.model_validate({
            "type": type, "status": EventStatus.NEW, "payload": payload
        }))

    def collect_events(self) -> Iterator[EventT]:
        """Собирает и возвращает все накопленные события"""
        while self._events:
            yield self._events.pop(0)


class Room(AggregateRoot):
    created_by: UUID
    type: RoomType
    name: Name | None = None
    slug: Slug | None = None
    visibility: RoomVisibility
    created_at: CurrentDatetime
    member_count: NonNegativeInt
    settings: RoomSettings

    @classmethod
    def create(cls, command: CreateRoomCommand, created_by: UUID) -> Self:
        room = cls(
            created_by=created_by,
            type=command.type,
            name=command.name,
            slug=command.slug,
            visibility=command.visibility,
            members_count=len(command.initial_users) + 1,
            settings=configure_default_room_settings(command.type, command.visibility),
        )
        cls._register_event(
            type="room_created",
            payload=RoomCreated.model_validate({
                **room.model_dump(),
                "initial_users": command.initial_users,
                "roles": ...,
            })
        )
        return ...

    @classmethod
    def _define_roles(cls, type: RoomType) -> list[Role]:  # noqa: A002
        owner_role = Role(type=..., name="owner", priority=100, permissions=...)
        match type:
            case RoomType.DIRECT:
                ...
            case RoomType.GROUP:
                ...
            case RoomType.CHANNEL:
                ...

    def add_member(self, member: ...) -> ...:
        ...


class RoomRole(BaseModel):
    """Роль пользователя в конкретной комнате с набором разрешений.
    Объединяет роль и её разрешения для обеспечения целостности правил доступа.
    """
    room_id: UUID
    role: Role
    permissions: list[Permission]

    def add_permission(self, permission: Permission) -> None:
        """Добавляет разрешение в роль, если его ещё нет.

        :param permission: Сущность разрешения.
        """
        if permission not in self.permissions:
            self.permissions.append(permission)

    def has_permission(self, permission_code: PermissionCode) -> bool:
        """Проверяет наличие конкретного разрешения к роли.

        :param permission_code: Уникальный код разрешения конкретного действия.
        """
        return any(permission.code == permission_code for permission in self.permissions)
