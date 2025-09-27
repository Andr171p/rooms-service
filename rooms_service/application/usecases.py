from ..domain.entities import Room
from .dto import RoomCreate


class CreateRoomUseCase:
    def __init__(self) -> None:
        ...

    async def execute(self, room_create: RoomCreate) -> Room:
        ...
