from __future__ import annotations

from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from .value_objects import PermissionCode, RoomSettings, RoomType, RoomVisibility, SystemRole

from datetime import datetime

import pytz

from .constants import DEFAULT_CHANNEL_MEMBERS, DEFAULT_DIRECT_MEMBERS, DEFAULT_GROUP_MEMBERS

moscow_tz = pytz.timezone("Europe/Moscow")


def current_datetime() -> datetime:
    """Получает текущее время (учитывает текущий часовой пояс)"""
    return datetime.now(moscow_tz)


def get_max_members_by_room(room_type: RoomType) -> int:
    """Получение максимального числа участника для комнаты по её типу.

    :param room_type: Тип комнаты.
    """
    from .value_objects import RoomType  # noqa: PLC0415

    room_type_to_max_members_map: dict[RoomType, int] = {
        RoomType.DIRECT: DEFAULT_DIRECT_MEMBERS,
        RoomType.CHANNEL: DEFAULT_CHANNEL_MEMBERS,
        RoomType.GROUP: DEFAULT_GROUP_MEMBERS,
    }
    return room_type_to_max_members_map[room_type]


def get_default_system_role_by_room(room_type: RoomType) -> SystemRole:
    """Получение системной роли по умолчанию для присоединившегося участника комнаты.

    :param room_type: Тип комнаты.
    """
    from .value_objects import SystemRole  # noqa: PLC0415

    room_type_to_default_system_role_map: dict[RoomType, SystemRole] = {
        RoomType.DIRECT: SystemRole.MEMBER,
        RoomType.GROUP: SystemRole.MEMBER,
        RoomType.CHANNEL: SystemRole.GUEST,
    }
    return room_type_to_default_system_role_map[room_type]


def configure_default_room_settings(
        room_type: RoomType, visibility: RoomVisibility
) -> RoomSettings:
    """Конфигурирует настройки комнаты по умолчанию.

    :param room_type: Тип комнаты.
    :param visibility: Видимость комнаты.
    :return Сконфигурированные настройки комнаты.
    """
    from .value_objects import (  # noqa: PLC0415
        JoinPermission,
        RoomMediaSettings,
        RoomMembersSettings,
        RoomMessagesSettings,
    )

    join_permission = (
        JoinPermission.APPROVAL if visibility == RoomVisibility.PRIVATE else JoinPermission.OPEN
    )
    return RoomSettings(
        messages=RoomMessagesSettings(
            allow_forwarding=not RoomVisibility.PRIVATE,
        ),
        members=RoomMembersSettings(
            max_members=get_max_members_by_room(room_type),
            join_permission=join_permission
        ),
        media=RoomMediaSettings(),
    )


# Права для гостя
GUEST_PERMISSIONS: Final[set[PermissionCode]] = {
    PermissionCode("message:read"),
    PermissionCode("message:react"),
}
# Права участника
MEMBER_PERMISSIONS: Final[set[PermissionCode]] = GUEST_PERMISSIONS | {
    PermissionCode("message:send"),
    PermissionCode("message:pin"),
    PermissionCode("media:send"),
    PermissionCode("member:add"),
}
# Права админа
ADMIN_PERMISSIONS: Final[set[PermissionCode]] = MEMBER_PERMISSIONS | {
    PermissionCode("member:ban"),
    PermissionCode("member:kick"),
    PermissionCode("member:mute"),
    PermissionCode("member:invite"),
}
# Права для владельца ('owner')
OWNER_PERMISSIONS: Final[set[PermissionCode]] = {
    PermissionCode("room:manage"),
    PermissionCode("role:manage"),
    PermissionCode("role:create"),
}
