from uuid import uuid4

from rooms_service.application.commands import CreateRoomCommand
from rooms_service.application.dto import RoomCreate
from rooms_service.domain.value_objects import RoomType, RoomVisibility

command = CreateRoomCommand(
    name="room",
    slug="room",
    type=RoomType.GROUP,
    visibility=RoomVisibility.PUBLIC,
    initial_users=[uuid4() for _ in range(5)],
)

room_create = RoomCreate.model_validate({**command.model_dump(), "created_by": uuid4()})

print(room_create)