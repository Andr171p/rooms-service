from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute
from dishka.integrations.fastapi import FromDishka as Depends
from fastapi import APIRouter, status
from fastauth import CurrentUser

from ...core.base import UnitOfWork
from ...core.commands import CreateRoomCommand
from ...core.domain import Room
from ...handlers import CreateRoomCommandHandler
from ..depends import RequirePermission

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
    return await handler.handle(command, created_by=current_user.x_user_id)


@rooms_router.get(
    path="/{id}",
    status_code=status.HTTP_200_OK,
    response_model=Room,
    summary="Получение комнаты по её уникальному идентификатору"
)
async def get_room(id: UUID, uow: Depends[UnitOfWork]) -> Room:  # noqa: A002
    return await uow.room_repository.read(id)


@rooms_router.patch(
    path="/{id}",
    status_code=status.HTTP_200_OK,
    response_model=Room,
    summaru="Модифицирует комнату"
)
async def update_room(id: UUID) -> ...: ...  # noqa: A002


@rooms_router.delete(
    path="/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаляет комнату",
    dependencies=[RequirePermission("room:delete")]
)
async def delete_room(id: UUID) -> None: ...  # noqa: A002
