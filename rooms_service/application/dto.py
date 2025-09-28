from abc import ABC
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from ..domain.value_objects import (
    Id,
    MemberStatus,
    Name,
    Nickname,
    RoomType,
    RoomVisibility,
    Slug,
)


class _DTO(BaseModel, ABC):
    model_config = ConfigDict(from_attributes=True, frozen=True)


class MemberCreate(_DTO):
    """Необходимые данные для создания участника"""
    id: Id
    user_id: UUID
    room_id: UUID
    role_id: UUID
    nickname: Nickname
    status: MemberStatus = MemberStatus.ACTIVE


class InitialMember(_DTO):
    user_id: UUID
    role_id: UUID
    nickname: Nickname | None = None
    status: MemberStatus = MemberStatus.ACTIVE


class RoomCreate(_DTO):
    """Команда для создания комнаты.

        Attributes:
            created_by: Создатель комнаты.
            name: Имя комнаты (придумывает пользователь).
            slug: Человеко-читаемый псевдоним для URL адреса
            (задаётся пользователем или генерируется автоматически)
            type: Тип создаваемой комнаты.
            visibility: Видимость комнаты для других пользователей.
            members: Участники, которых нужно добавить в комнату.
        """
    created_by: UUID
    name: Name
    slug: Slug
    type: RoomType
    visibility: RoomVisibility
    members: list[InitialMember]
