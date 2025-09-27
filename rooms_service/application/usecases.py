from uuid import UUID

from ..domain.entities import Member, Room
from ..domain.rules import get_default_system_role_by_room
from ..domain.value_objects import Name
from .commands import CreateRoomCommand
from .dto import MemberCreate, RoomCreate
from .repositories import UnitOfWork


class CreateRoomUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, command: CreateRoomCommand, created_by: UUID) -> Room:
        return ...
