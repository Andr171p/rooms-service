from typing import Self

from abc import ABC
from collections.abc import Iterator
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt

from .commands import CreateRoomCommand
from .entities import Permission, Role
from .events import Event, EventT, RoomCreated
from .value_objects import (
    CurrentDatetime,
    EventStatus,
    Id,
    Name,
    PermissionCode,
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

    def _register_event(self, event: EventT) -> None:
        self._events.append(event)

    def collect_events(self) -> Iterator[EventT]:
        """Собирает и возвращает все накопленные события"""
        while self._events:
            yield self._events.pop(0)


class Room(AggregateRoot):
    created_by: UUID
    type: RoomType
    name: Name | None = None
    slug: Slug | None = None
    visibility: RoomVisibility = RoomVisibility.PUBLIC
    created_at: CurrentDatetime
    members_count: NonNegativeInt

    @classmethod
    def create(cls, command: CreateRoomCommand, created_by: UUID) -> Self:
        room = cls(
            created_by=created_by,
            type=command.type,
            name=command.name,
            slug=command.slug,
            visibility=command.visibility,
            members_count=len(command.initial_users) + 1
        )
        room_created_event = Event(
            type="room_created",
            status=EventStatus.NEW,
            payload=RoomCreated.model_validate(room)
        )
        cls._register_event(room_created_event)
        return ...

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
