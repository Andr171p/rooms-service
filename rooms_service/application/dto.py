from abc import ABC
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from ..domain.value_objects import CurrentDatetime, MemberStatus


class _DTO(BaseModel, ABC):
    model_config = ConfigDict(from_attributes=True, frozen=True)


class MemberCreate(_DTO):
    """Необходимые данные для создания участника"""
    user_id: UUID
    room_id: UUID
    role_id: UUID
    status: MemberStatus = MemberStatus.ACTIVE
    joined_at: CurrentDatetime
