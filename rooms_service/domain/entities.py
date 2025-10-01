from __future__ import annotations

from abc import ABC
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .value_objects import (
    CurrentDatetime,
    Id,
    MemberStatus,
    Nickname,
    Role,
)


class _Entity(BaseModel, ABC):
    id: Id

    model_config = ConfigDict(from_attributes=True)


class Member(_Entity):
    """Участник комнаты.

    Attributes:
        id: Уникальный идентификатор участника.
        user_id: Идентификатор пользователя в системе.
        room_id: Идентификатор комнаты.
        role: Роль которая выдана пользователю.
        status: Статус участника.
        joined_at: Дата присоединения пользователя к комнате.
    """
    user_id: UUID
    room_id: UUID
    role: Role
    nickname: Nickname
    status: MemberStatus = MemberStatus.ACTIVE
    joined_at: CurrentDatetime
