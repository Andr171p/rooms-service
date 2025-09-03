from datetime import datetime
from uuid import UUID

import pytz

from .constants import TYPE_TO_MAX_MEMBERS_MAPPING
from .enums import MediaType, RoomType
from .properties import RoomProperties

moscow_tz = pytz.timezone("Europe/Moscow")


def current_datetime() -> datetime:
    """Получает текущее время (учитывает текущий часовой пояс)"""
    return datetime.now(moscow_tz)


def all_media_types() -> list[MediaType]:
    """Возвращает все доступные типы медиа"""
    return [media_type.value for media_type in MediaType]


def configure_default_room_properties(id: UUID, type: RoomType) -> RoomProperties:  # noqa: A002
    """Конфигурирует настройки комнаты по умолчанию"""
    max_members = TYPE_TO_MAX_MEMBERS_MAPPING[type]
    return RoomProperties(room_id=id, max_members=max_members)
