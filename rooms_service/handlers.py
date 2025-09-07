from .core.base import CommandHandler, UnitOfWork
from .core.cqrs import CreateRoomCommand
from .core.domain import Member, Room


class CreateRoomCommandHandler(CommandHandler[Room]):
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self.unit_of_work = unit_of_work

    async def handle(self, command: CreateRoomCommand, **kwargs) -> Room:
        creator_by = kwargs.get("creator_by")
        if creator_by is None:
            raise ValueError("'creator_by' must be provided!")
        async with self.unit_of_work as uow:
            room = Room.model_validate({
                "creator_by": creator_by, **command.model_dump(exclude={"initial_members"})
            })
            created_room = await uow.room_repository.create(room)
            members = [
                Member(
                    user_id=initial_member,
                    room_id=created_room.id,
                    role_id=...,
                )
                for initial_member in command.initial_members
            ]
            await uow.member_repository.bulk_create(members)
            await uow.commit()
        return ...
