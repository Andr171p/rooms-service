from __future__ import annotations

from abc import ABC
from uuid import UUID

from pydantic import BaseModel, ConfigDict, NonNegativeInt

from ..domain.value_objects import (
    CurrentDatetime,
    Id,
    MemberStatus,
    Name,
    Nickname,
    Role,
    RoomType,
    RoomVisibility,
    Slug,
)


class _DTO(BaseModel, ABC):
    model_config = ConfigDict(from_attributes=True, frozen=True)


class RoomCreate(_DTO):
    """Создание комнаты"""
    created_by: UUID
    type: RoomType
    name: Name | None = None
    slug: Slug | None = None
    visibility: RoomVisibility
    created_at: CurrentDatetime
    member_count: NonNegativeInt
    members: list[MemberAdd]
    roles: list[Role]


class MemberAdd(_DTO):
    """Необходимые данные для создания участника"""
    id: Id
    user_id: UUID
    room_id: UUID
    role_name: Name
    nickname: Nickname
    status: MemberStatus = MemberStatus.ACTIVE
    joined_at: CurrentDatetime
