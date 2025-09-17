from typing import Any, TypeVar

import asyncio
import logging
from collections.abc import Callable, Coroutine
from datetime import datetime, timedelta
from functools import wraps

import pytz
from pydantic import NonNegativeInt, PositiveInt

from .constants import TYPE_TO_MAX_MEMBERS_MAP, JoinPermission, RoomType, RoomVisibility
from .value_objects import (
    RoomMediaSettings,
    RoomMembersSettings,
    RoomMessagesSettings,
    RoomSettings,
)

T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])
AsyncFunc = Callable[..., Coroutine[Any, Any, Any]]

logger = logging.getLogger(__name__)

moscow_tz = pytz.timezone("Europe/Moscow")


def current_datetime() -> datetime:
    """Получает текущее время (учитывает текущий часовой пояс)"""
    return datetime.now(moscow_tz)


def schedule(interval: timedelta) -> Callable[[F], F]:
    """Декоратор для периодического выполнения асинхронной функции"""
    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            sleep = interval.total_seconds()
            logger.info("Scheduling %s every %s seconds", func.__name__, sleep)
            while True:
                try:
                    logger.debug("Running scheduling task: %s", func.__name__)
                    await func(*args, **kwargs)
                    logger.debug("Completed scheduling task: %s", func.__name__)
                except asyncio.CancelledError:
                    logger.warning("Task %s canceled", func.__name__)
                    raise
                finally:
                    await asyncio.sleep(sleep)
        return wrapper
    return decorator


def configure_default_room_settings(
        room_type: RoomType, visibility: RoomVisibility
) -> RoomSettings:
    """Конфигурирует настройки комнаты по умолчанию.

    :param room_type: Тип комнаты.
    :param visibility: Видимость комнаты.
    :return Сконфигурированные настройки комнаты.
    """
    join_permission = (
        JoinPermission.APPROVAL if visibility == RoomVisibility.PRIVATE else JoinPermission.OPEN
    )
    return RoomSettings(
        messages=RoomMessagesSettings(
            allow_forwarding=not RoomVisibility.PRIVATE,
        ),
        members=RoomMembersSettings(
            max_members=TYPE_TO_MAX_MEMBERS_MAP[room_type],
            join_permission=join_permission
        ),
        media=RoomMediaSettings(),
    )


def total_pages(total_count: NonNegativeInt, limit: PositiveInt) -> int:
    """Рассчитывает общее количество страниц по общему количеству и лимиту

    :param total_count: Общее количество.
    :param limit: Ограничение элементов на странице.
    :return Количество страниц
    """
    if total_count % limit != 0:
        return total_count // limit + 1
    return total_count // limit
