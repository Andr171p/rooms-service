from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .constants import EventStatus
from .utils import current_datetime


class Event(BaseModel):
    """Базовая модель события"""
    id: UUID = Field(default_factory=uuid4)
    type: str
    status: EventStatus
    created_at: datetime = Field(default_factory=current_datetime)
