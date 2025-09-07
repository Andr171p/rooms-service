from dishka.integrations.fastapi import DishkaRoute
from dishka.integrations.fastapi import FromDishka as Depends
from fastapi import APIRouter, status
from fastauth import CurrentUser

from ...core.domain import Room
from ..schemas import RoomCreateSchema

rooms_router = APIRouter(prefix="/rooms", tags=["Rooms"], route_class=DishkaRoute)


@rooms_router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    response_model=Room,
    summary="Создание комнаты",
)
async def create_room(room_create: RoomCreateSchema, current_user: CurrentUser) -> ...:
    ...
