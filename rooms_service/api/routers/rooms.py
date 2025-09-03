from dishka.integrations.fastapi import DishkaRoute
from dishka.integrations.fastapi import FromDishka as Depends
from fastapi import APIRouter, status
from fastauth import CurrentUser

from ...core.domain import Room
from ...core.utils import configure_default_room_properties
from ..schemas import RoomCreate

rooms_router = APIRouter(prefix="/rooms", tags=["Rooms"], route_class=DishkaRoute)


@rooms_router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    response_model=Room,
    summary="Создаёт комнату",
)
async def create_room(room_create: RoomCreate, current_user: CurrentUser) -> ...:
    room = Room(
        created_by=current_user.id,
        type=room_create.type,
        name=room_create.name,
        properties=configure_default_room_properties()
    )
