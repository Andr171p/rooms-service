from abc import ABC
from uuid import UUID

from ..domain.aggragates import Room
from ..domain.commands import CreateRoomCommand
from ..domain.events import Event, EventT, MembersAdded, RoomCreated
from .dto import MemberAdd, RoomCreate
from .eventbus import EventBus
from .repositories import RoomRepository


class UseCase(ABC):
    _eventbus: "EventBus"

    async def _publish_events(self, events: list[EventT]) -> None:
        for event in events:
            await self._eventbus.publish(event)


class CreateRoomUseCase(UseCase):
    """Реализация сценария создания комнаты"""
    def __init__(self, repository: RoomRepository, eventbus: EventBus) -> None:
        self._repository = repository
        self._eventbus = eventbus

    async def execute(self, command: CreateRoomCommand, created_by: UUID) -> Room:
        room = Room.create(command, created_by)
        for event in room.collect_events():
            if event.type == "room_created" and isinstance(event.payload, RoomCreated):
                await self._repository.create(RoomCreate.model_validate(event.payload), created_by)
            elif event.type == "members_added" and isinstance(event.payload, MembersAdded):
                await self._repository.add_members(
                    [MemberAdd.model_validate(member) for member in event.payload.members]
                )
        return ...
