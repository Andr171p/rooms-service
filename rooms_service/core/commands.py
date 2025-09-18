from typing import Self

from abc import ABC
from uuid import UUID

from pydantic import BaseModel, model_validator

from .constants import RoomType, RoomVisibility
from .value_objects import Name, Slug


class Command(ABC, BaseModel):
    """Абстрактный класс для создания команды"""


class CreateRoomCommand(Command):
    """Команда для создания комнаты"""
    creator_by: UUID
    name: Name
    slug: Slug
    type: RoomType
    visibility: RoomVisibility
    initial_users: list[UUID]

    @model_validator(mode="after")
    def validate_initial_users(self) -> Self:
        if self.type == RoomType.DIRECT and len(self.initial_users) != 1:
            raise ValueError("Invalid member count!")
        return self


class UpdateRoomCommand(Command):
    """Команда для обновления комнаты"""


class DeleteRoomCommand(Command):
    """Команда для удаления комнаты"""
    id: UUID
