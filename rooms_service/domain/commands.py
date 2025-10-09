from abc import ABC
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .value_objects import Name, RoomType, RoomVisibility, Slug


class Command(BaseModel, ABC):
    """Абстрактный класс для создания команды"""

    model_config = ConfigDict(from_attributes=True, frozen=True)


class CreateRoomCommand(Command):
    """Команда для создания комнаты.

    Attributes:
        name: Имя комнаты (придумывает пользователь).
        slug: Человеко-читаемый псевдоним для URL адреса
        (задаётся пользователем или генерируется автоматически)
        type: Тип создаваемой комнаты.
        visibility: Видимость комнаты для других пользователей.
        initial_users: Пользователи, которых нужно добавить в комнату.
    """
    name: Name
    slug: Slug
    type: RoomType
    visibility: RoomVisibility
    initial_users: list[UUID]


class AddMembersCommand(Command):
    """Команда для добавления участников в комнату.

    Attributes:
        users: Пользователи, которых нужно добавить.
    """
    users: list[UUID] = Field(
        default_factory=list, description="Пользователи, которых нужно добавить"
    )
