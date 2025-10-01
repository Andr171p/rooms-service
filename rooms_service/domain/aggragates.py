from typing import Self

from abc import ABC
from collections.abc import Iterator
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt

from ..core.domain import Member
from .commands import CreateRoomCommand
from .events import Event, EventT, PayloadT, RoomCreated
from .rules import ROLES_REGISTRY, configure_default_room_settings
from .value_objects import (
    CurrentDatetime,
    EventStatus,
    EventType,
    Id,
    Name,
    Permission,
    Role,
    RoomSettings,
    RoomType,
    RoomVisibility,
    Slug,
    SystemRole,
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
        owner = Member.model_validate({
            "user_id": created_by,
            "room_id": room.id,
            "role": ROLES_REGISTRY[SystemRole.OWNER],
            "nickname": "empty",
        })
        members: list[Member] = [
            Member.model_validate({
                "user_id": initial_user,
                "room_id": room.id,
                "role": cls._define_role(room.type),
                "nickname": "empty",
            })
            for initial_user in command.initial_users
        ]
        members.append(owner)
        cls._register_event(
            type="room_created",
            payload=RoomCreated.model_validate({**room.model_dump(), "members": members[::-1]})
        )
        return room

    @staticmethod
    def _define_role(type: RoomType) -> Role:  # noqa: A002
        match type:
            case RoomType.DIRECT, RoomType.GROUP:
                return ROLES_REGISTRY[SystemRole.MEMBER]
            case RoomType.CHANNEL:
                return ROLES_REGISTRY[SystemRole.GUEST]

    def add_member(self, user_id: UUID) -> Member:
        """Добавляет пользователя в комнату"""

    def create_custom_role(self, name: Name, permissions: list[Permission]) -> Role:
        """Создаёт кастомную роль внутри комнаты"""
