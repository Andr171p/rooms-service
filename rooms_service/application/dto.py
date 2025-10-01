from abc import ABC
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from ..domain.value_objects import (
    CurrentDatetime,
    Id,
    MemberStatus,
    Name,
    Nickname,
)


class _DTO(BaseModel, ABC):
    model_config = ConfigDict(from_attributes=True, frozen=True)


class MemberAdd(_DTO):
    """Необходимые данные для создания участника"""
    id: Id
    user_id: UUID
    room_id: UUID
    role_name: Name
    nickname: Nickname
    status: MemberStatus = MemberStatus.ACTIVE
    joined_at: CurrentDatetime
