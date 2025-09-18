from .core.base import CommandHandler, UnitOfWork
from .core.commands import CreateRoomCommand
from .core.constants import ROOM_TYPE_TO_SYSTEM_ROLE_MAP
from .core.domain import Member, RolePermissions, Room
from .core.events import OutboxEvent, RoomCreatedEvent


class CreateRoomCommandHandler(CommandHandler[Room]):
    """Обработчик команды создания комнаты"""
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def handle(self, command: CreateRoomCommand, **kwargs) -> Room:
        created_by = kwargs.get("created_by")
        if created_by is None:
            raise ValueError("'creator_by' must be provided!")
        async with self.uow.transaction() as uow:
            room = Room.model_validate({
                "created_by": created_by, **command.model_dump(exclude={"initial_members_ids"})
            })
            created_room = await uow.room_repository.create(room)
            owner_role = await uow.role_repository.get_by_name("owner")
            owner = Member(
                user_id=created_room.created_by, room_id=created_room.id, role_id=owner_role.id
            )
            default_system_role = await uow.role_repository.get_by_name(
                ROOM_TYPE_TO_SYSTEM_ROLE_MAP[created_room.type]
            )
            initial_members = [
                Member(
                    user_id=initial_user,
                    room_id=created_room.id,
                    role_id=default_system_role.id,
                )
                for initial_user in command.initial_users
            ]
            initial_members.append(owner)
            await uow.member_repository.bulk_create(initial_members)
            roles_permissions = await uow.room_repository.get_roles_permissions(created_room.id)
            outbox_event = self._prepare_outbox_event(
                created_room, initial_members, roles_permissions
            )
            await uow.outbox_repository.create(outbox_event)
            await uow.commit()
        return created_room

    @staticmethod
    def _prepare_outbox_event(
            created_room: Room,
            initial_members: list[Member],
            roles_permissions: list[RolePermissions]
    ) -> OutboxEvent:
        event = RoomCreatedEvent.model_validate({
            **created_room.model_dump(),
            "members": initial_members,
            "roles_permissions": roles_permissions
        })
        return OutboxEvent(
            aggregate_id=created_room.id,
            aggregate_type=created_room.__class__.__name__,
            event_type=event.event_type,
            payload=event.model_dump(),
            event_status=event.event_status,
        )
