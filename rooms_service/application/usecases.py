from typing import Any

from uuid import UUID

from ..domain.aggragates import Room
from ..domain.commands import CreateRoomCommand
from ..domain.events import Event
from .dto import RoomCreate
from .eventbus import EventBus
from .repositories import RoomRepository


class CreateRoomUseCase:
    """Реализация сценария создания комнаты"""
    def __init__(self, repository: RoomRepository, eventbus: EventBus) -> None:
        self._repository = repository
        self._eventbus = eventbus

    async def execute(self, command: CreateRoomCommand, created_by: UUID) -> Room:
        room = Room.create(command, created_by)
        values: dict[str, Any] = {}
        events: list[Event] = []
        for event in room.collect_events():
            match event.type:
                case "room_created":
                    values.update(event.payload.model_dump())
                case "member_added":
                    if values["version"] == event.payload.version:
                        values["members"] = event.payload.model_dump(exclude={"version"})
            events.append(event)
        room_create = RoomCreate.model_validate(values)
        created_room = await self._repository.create(room_create)
        for event in events:
            await self._eventbus.publish(event)
        return created_room
