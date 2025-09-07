from .core.base import CommandHandler
from .core.cqrs import CreateRoomCommand
from .core.domain import Room
from .database.repository import RoomRepository


class CreateRoomCommandHandler(CommandHandler[Room]):
    def __init__(self, repository: RoomRepository) -> None:
        self.repository = repository

    async def handle(self, command: CreateRoomCommand, **kwargs) -> Room:
        creator_by = kwargs.get("creator_by")
        if creator_by is None:
            raise ValueError("user_id must be provided!")
        room = Room.model_validate({"creator_by": creator_by, **command.model_dump()})
        return await self.repository.create(room)
