from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from ..domain.rules import current_datetime
from ..domain.value_objects import MemberStatus


class _DTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MemberCreate(_DTO):
    """Создание пользователя"""
    user_id: UUID
    room_id: UUID
    role_id: UUID
    status: MemberStatus = MemberStatus.ACTIVE
    joined_at: datetime = Field(default_factory=current_datetime)
