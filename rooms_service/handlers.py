from .core.base import CommandHandler, UnitOfWork
from .core.commands import CreateRoomCommand
from .core.constants import TYPE_TO_SYSTEM_ROLE_MAP
from .core.domain import Member, Room


class CreateRoomCommandHandler(CommandHandler[Room]):
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def handle(self, command: CreateRoomCommand, **kwargs) -> Room:
        created_by = kwargs.get("created_by")
        if created_by is None:
            raise ValueError("'creator_by' must be provided!")
        async with self.uow.transaction() as uow:
            room = Room.model_validate({
                "created_by": created_by, **command.model_dump(exclude={"initial_members"})
            })
            created_room = await uow.room_repository.create(room)
            owner_role = await uow.role_repository.get_by_name("owner")
            owner = Member(
                user_id=created_room.created_by, room_id=created_room.id, role_id=owner_role.id
            )
            default_role = await uow.role_repository.get_by_name(
                TYPE_TO_SYSTEM_ROLE_MAP[created_room.type]
            )
            members = [
                Member(
                    user_id=initial_member,
                    room_id=created_room.id,
                    role_id=default_role.id,
                )
                for initial_member in command.initial_members
            ]
            members.append(owner)
            await uow.member_repository.bulk_create(members)
            await uow.commit()
        return created_room
