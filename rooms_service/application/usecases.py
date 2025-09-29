from uuid import UUID

from ..domain.entities import Room
from ..domain.rules import get_default_system_role_by_room
from ..domain.value_objects import SystemRole
from rooms_service.domain.commands import CreateRoomCommand
from .dto import InitialMember, RoomCreate
from .repositories import UnitOfWork


class CreateRoomUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, command: CreateRoomCommand, created_by: UUID) -> Room:
        default_system_role_name = get_default_system_role_by_room(command.type)
        async with self._uow.transaction():
            owner_role = await self._uow.role_repository.get_system(SystemRole.OWNER)
            default_role = await self._uow.role_repository.get_system(default_system_role_name)
            initial_members: list[InitialMember] = [
                InitialMember(user_id=initial_user, role_id=default_role.id)
                for initial_user in command.initial_users
            ]
            initial_members.append(InitialMember(user_id=created_by, role_id=owner_role.id))
            room_create = RoomCreate.model_validate({
                **command.model_dump(exclude={"initial_users"}),
                "created_by": created_by,
                "members": initial_members[::-1]  # Owner в начале списка
            })
            created_room = await self._uow.room_repository.create(room_create)
            await self._uow.commit()
        return created_room
