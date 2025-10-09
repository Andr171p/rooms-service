from abc import ABC
from uuid import UUID

from ..domain.aggragates import AggregateRoot, Room
from ..domain.commands import AddMembersCommand, CreateRoomCommand
from ..domain.entities import Member
from .dto import MemberAdd, RoomCreate
from .eventbus import EventBus
from .repositories import RoomRepository


class UseCase(ABC):
    _eventbus: "EventBus"

    async def _publish_events(self, aggregate_root: AggregateRoot) -> None:
        for event in aggregate_root.collect_events():
            await self._eventbus.publish(event)


class CreateRoomUseCase(UseCase):
    """Реализация сценария создания комнаты"""
    def __init__(self, repository: RoomRepository, eventbus: EventBus) -> None:
        self._repository = repository
        self._eventbus = eventbus

    async def execute(self, command: CreateRoomCommand, created_by: UUID) -> Room:
        room = Room.create(command, created_by)
        members = room.add_members(command.initial_users)
        room_create = RoomCreate.model_validate({
            **room.model_dump(),
            "members": [
                MemberAdd.model_validate({
                    **room.model_dump(exclude={"role"}), "role_name": member.role.name
                })
                for member in members]
        })
        created_room = await self._repository.create(room_create)
        await self._publish_events(room)
        return created_room


class AddMembersUseCase(UseCase):
    """Реализация сценария добавления участников в комнату"""
    def __init__(self, repository: RoomRepository, eventbus: EventBus) -> None:
        self._repository = repository
        self._eventbus = eventbus

    async def execute(self, command: AddMembersCommand, room_id: UUID) -> list[Member]:
        room = await self._repository.read(room_id)
        members = room.add_members(command.users)
        members_add = [
            MemberAdd.model_validate({
                **member.model_dump(exclude={"role"}), "role_name": member.role.name
            })
            for member in members
        ]
        await self._repository.add_members(members_add)
        await self._publish_events(room)
        return members
