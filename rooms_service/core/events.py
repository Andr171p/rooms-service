from typing import Any

import time
from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, NonNegativeInt, computed_field

from .constants import SOURCE, EventStatus, RoomType, RoomVisibility
from .domain import Member, Role, RolePermissions
from .utils import current_datetime, generate_correlation_id
from .value_objects import Name, RoomSettings, Slug


class Event(BaseModel):
    """Базовая модель события

    Attributes:
        event_id: Уникальный идентификатор события.
        event_type: Тип события, например: send_message, create_room, ...
        event_status: Текущий статус события.
        source: Источник публикуемого события.
        correlation_id: ID для трассировки события между микро-сервисами.
        created_at: Время создания события.
    """
    event_id: UUID = Field(default_factory=uuid4)
    event_type: str
    event_status: EventStatus = EventStatus.NEW
    source: str = SOURCE
    correlation_id: str = Field(default_factory=lambda: generate_correlation_id(SOURCE))
    created_at: datetime = Field(default_factory=current_datetime)


class OutboxEvent(Event):
    """Модель события для реализации Outbox паттерна"""
    aggregate_id: UUID
    aggregate_type: str
    payload: dict[str, Any]
    retries: NonNegativeInt = Field(default=0)

    @computed_field(description="Предотвращение обработки дубликатов события")
    def dedup_key(self) -> str:
        return f"{time.time()}-{self.aggregate_type}-{self.aggregate_id}"

    @computed_field(description="Гарантия порядка обработки события для одного агрегата")
    def partition_key(self) -> str:
        return f"{self.aggregate_type}-{self.aggregate_id}"


class RoomCreatedEvent(Event):
    """Комната создана"""
    event_type: str = "room_created"

    id: UUID
    name: Name
    type: RoomType
    slug: Slug
    created_by: UUID
    visibility: RoomVisibility
    settings: RoomSettings
    members: list[Member]
    roles: list[Role]
    roles_permissions: list[RolePermissions]
