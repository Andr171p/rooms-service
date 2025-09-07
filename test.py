from uuid import uuid4

from rooms_service.core.constants import RoomType
from rooms_service.core.domain import Room
from rooms_service.core.value_objects import Name

room = Room(
    created_by=uuid4(),
    type=RoomType.CHANNEL,
    name="ВШЦТ",
)

print(room)


print(Name(101 * "a"))
