from typing import Self

from abc import ABC
from collections.abc import Iterator
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt, computed_field

from .commands import CreateRoomCommand
from .entities import Member
from .events import Event, EventT, MembersAdded, PayloadT, RoomCreated
from .rules import ROLES_REGISTRY
from .value_objects import (
    CurrentDatetime,
    EventStatus,
    EventType,
    Id,
    JoinPermission,
    Name,
    Role,
    RoomMediaSettings,
    RoomMembersSettings,
    RoomMessagesSettings,
    RoomSettings,
    RoomType,
    RoomVisibility,
    Slug,
    SystemRole,
)


class AggregateRoot(BaseModel, ABC):
    id: Id
    _events: list[EventT] = Field(default_factory=list, exclude=True)
    _version: int = Field(default=1, exclude=True)

    model_config = ConfigDict(
        arbitrary_types_allowed=True, validate_assignment=True, frozen=False
    )

    @property
    def version(self) -> int:
        """Текущая версия агрегата"""
        return self._version

    def _increment_version(self) -> None:
        """Увеличение версии агрегата"""
        self._version += 1

    def _register_event(self, type: EventType, payload: PayloadT) -> None:  # noqa: A002
        """Регистрирует доменное событие"""
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
    roles: list[Role]

    @computed_field(description="Настройки комнаты")
    @property
    def settings(self) -> RoomSettings:
        return self.configure_default_room_settings(self.visibility)

    @classmethod
    def create(cls, command: CreateRoomCommand, created_by: UUID) -> Self:
        room = cls(
            created_by=created_by,
            type=command.type,
            name=command.name,
            slug=command.slug,
            visibility=command.visibility,
            member_count=len(command.initial_users) + 1,
            roles=[ROLES_REGISTRY[SystemRole.OWNER], cls._define_default_role()]
        )
        cls._register_event(
            room, type=EventType("room_created"), payload=RoomCreated.model_validate({
                **room.model_dump(), "version": room.version
            })
        )
        return room

    def add_members(self, users: list[UUID]) -> list[Member]:
        """Добавляет участников в комнату

        :param users: Идентификаторы пользователей.
        :return Добавленные сущности пользователей.
        """
        members: list[Member] = [
            Member.model_validate({
                "user": user,
                "room_id": self.id,
                "role": self._define_default_role(self.type),
                "nickname": "empty"
            })
            for user in users
        ]
        self._register_event(
            type=EventType("members_added"), payload=MembersAdded(members=members)
        )
        self._increment_version()
        return members

    @staticmethod
    def _define_default_role(type: RoomType) -> Role:  # noqa: A002
        """Определяет системные роли по умолчанию для новых участников"""
        match type:
            case RoomType.DIRECT, RoomType.GROUP:
                return ROLES_REGISTRY[SystemRole.MEMBER]
            case RoomType.CHANNEL:
                return ROLES_REGISTRY[SystemRole.GUEST]

    @staticmethod
    def configure_default_room_settings(visibility: RoomVisibility) -> RoomSettings:
        """Конфигурирует настройки комнаты по умолчанию.

        :param visibility: Видимость комнаты.
        :return Сконфигурированные настройки комнаты.
        """
        join_permission = (
            JoinPermission.APPROVAL
            if visibility == RoomVisibility.PRIVATE
            else JoinPermission.OPEN
        )
        return RoomSettings(
            messages=RoomMessagesSettings(
                allow_forwarding=not RoomVisibility.PRIVATE,
            ),
            members=RoomMembersSettings(join_permission=join_permission),
            media=RoomMediaSettings(),
        )
