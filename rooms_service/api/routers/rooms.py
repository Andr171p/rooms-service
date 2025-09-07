from dishka.integrations.fastapi import DishkaRoute
from dishka.integrations.fastapi import FromDishka as Depends
from fastapi import APIRouter, status
from fastauth import CurrentUser

from ...core.cqrs import CreateRoomCommand
from ...core.domain import Room
from ...handlers import CreateRoomCommandHandler

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
        handler: Depends[CreateRoomCommandHandler]
) -> Room:
    return await handler.handle(command, creator_by=current_user.x_user_id)
