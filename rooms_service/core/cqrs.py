from uuid import UUID

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
