from uuid import uuid4

from rooms_service.core.constants import RoomType
from rooms_service.core.domain import Room

room = Room(
    created_by=uuid4(),
    type=RoomType.CHANNEL,
    name="ВШЦТ",
)

print(room)