from datetime import datetime

import pytz

from .constants import TYPE_TO_MAX_MEMBERS_MAP, JoinPermission, RoomType, RoomVisibility
from .value_objects import (
    RoomMediaSettings,
    RoomMembersSettings,
    RoomMessagesSettings,
    RoomSettings,
)

moscow_tz = pytz.timezone("Europe/Moscow")


def current_datetime() -> datetime:
    """Получает текущее время (учитывает текущий часовой пояс)"""
    return datetime.now(moscow_tz)


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
