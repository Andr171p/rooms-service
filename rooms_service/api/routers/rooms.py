from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute
from dishka.integrations.fastapi import FromDishka as Depends
from fastapi import APIRouter, status
from fastauth import CurrentUser

from ...application.dto import MemberAdd
from ...application.usecases import CreateRoomUseCase
from ...domain.aggragates import Room
from ...domain.commands import CreateRoomCommand
from ...domain.value_objects import Role

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
    return await usecase.execute(command, created_by=current_user.x_user_id)


@rooms_router.post(
    path="/{room_id}/roles",
    status_code=status.HTTP_201_CREATED,
    response_model=...,
    summary="Создаёт кастомную роль внутри комнаты"
)
async def create_room_role(room_id: UUID, role: Role) -> ...: ...


@rooms_router.post(
    path="/{room_id}/members",
    status_code=status.HTTP_201_CREATED,
    response_model=...,
    summary="Добавляет участника в комнату"
)
async def add_member_to_room(room_id: UUID) -> ...: ...
