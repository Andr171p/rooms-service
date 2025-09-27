from dishka.integrations.fastapi import DishkaRoute
from dishka.integrations.fastapi import FromDishka as Depends
from fastapi import APIRouter, status
from fastauth import CurrentUser

from ...application.commands import CreateRoomCommand
from ...application.dto import RoomCreate
from ...application.usecases import CreateRoomUseCase
from ...domain.entities import Room

rooms_router = APIRouter(prefix="/rooms", tags=["Rooms"], route_class=DishkaRoute)


@rooms_router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    response_model=Room,
    summary="Создание комнаты",
)
async def create_room(
        command: CreateRoomCommand,
        current_user: CurrentUser,
        usecase: Depends[CreateRoomUseCase],
) -> Room:
    return await usecase.execute(RoomCreate.model_validate(
        {**command.model_dump(), "created_by": current_user.x_user_id}
    ))
