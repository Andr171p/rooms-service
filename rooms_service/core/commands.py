from typing import Self

from uuid import UUID

from pydantic import model_validator

from .base import Command
from .constants import RoomType, RoomVisibility
from .value_objects import Name, Slug


class CreateRoomCommand(Command):
    """Команда для создания комнаты"""
    creator_by: UUID
    name: Name
    slug: Slug
    type: RoomType
    visibility: RoomVisibility
    initial_members: list[UUID]

    @model_validator(mode="after")
    def validate_initial_members(self) -> Self:
        if self.type == RoomType.DIRECT and len(self.initial_members) != 1:
            raise ValueError("Invalid member count!")
        return self
