from typing import Annotated, TypeVar

from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from .constants import SOURCE
from .rules import current_datetime
from .value_objects import CorrelationId, CurrentDatetime, EventStatus, Id

PayloadType = TypeVar("PayloadType", bound=BaseModel)


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
    type: str
    status: EventStatus
    source: str = SOURCE
    payload: PayloadType
    correlation_id: DefaultCorrelationId
    created_at: CurrentDatetime

    model_config = ConfigDict(from_attributes=True, frozen=True)
