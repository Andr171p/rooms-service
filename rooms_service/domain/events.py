from typing import Annotated, TypeVar

import time
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt, computed_field

from ..shared import current_datetime
from .constants import SOURCE
from .value_objects import (
    CorrelationId,
    CurrentDatetime,
    EventStatus,
    EventType,
    Id,
    Name,
    Role,
    RoomSettings,
    RoomType,
    RoomVisibility,
    Slug,
)

PayloadT = TypeVar("PayloadT", bound=BaseModel)


def generate_correlation_id(source: str = SOURCE) -> str:
    """Генерирует уникальный ID для трассировки и дебагинга событий между сервисами"""
    return f"{source}--{current_datetime().microsecond}--{str(uuid4())[:8]}"


DefaultCorrelationId = Annotated[CorrelationId, Field(default_factory=generate_correlation_id)]


class Event(BaseModel):
    """Базовая модель события

    Attributes:
        id: Уникальный идентификатор события.
        type: Тип события, например: message_sent, room_created, ...
        status: Текущий статус события.
        source: Источник публикуемого события.
        payload: Данные передаваемые в событие.
        correlation_id: ID для трассировки события между микро-сервисами.
        created_at: Время создания события.
    """
    id: Id
    type: EventType
    status: EventStatus
    source: str = SOURCE
    payload: PayloadT
    correlation_id: DefaultCorrelationId
    created_at: CurrentDatetime

    model_config = ConfigDict(from_attributes=True, frozen=True)


EventT = TypeVar("EventT", bound=Event)


class OutboxEvent(Event):
    """Модель события для реализации Outbox паттерна.

    Attributes:
        aggregate_id: Идентификатор сущности, агрегата передаваемой в payload.
        aggregate_type: Тип сущности, например: Room, Member,... etc.
        retries: Количество попыток обработки события.
    """
    aggregate_id: UUID
    aggregate_type: str
    retries: NonNegativeInt = 0

    @computed_field(description="Предотвращение обработки дубликатов события")
    def dedup_key(self) -> str:
        return f"{time.time()}--{self.aggregate_type}--{self.aggregate_id}"

    @computed_field(description="Гарантия порядка обработки события для одного агрегата")
    def partition_key(self) -> str:
        return f"{self.aggregate_type}--{self.aggregate_id}"


class RoomCreated(BaseModel):
    id: UUID
    created_by: UUID
    type: RoomType
    name: Name | None = None
    slug: Slug | None = None
    visibility: RoomVisibility
    created_at: CurrentDatetime
    settings: RoomSettings
    member_count: NonNegativeInt
    roles: list[Role]
    version: NonNegativeInt


class MemberAdded(BaseModel):
    """Участник добавлен в комнату"""
    user_id: UUID
    room_id: UUID
    role_name: Name
    version: NonNegativeInt


class MembersAdded(BaseModel):
    """Массовое добавление участников в комнату"""
    members: list[MemberAdded]
    version: NonNegativeInt
