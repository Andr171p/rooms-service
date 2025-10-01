from __future__ import annotations

from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from .value_objects import PermissionCode, RoomSettings, RoomType, RoomVisibility, SystemRole

from datetime import datetime

import pytz

from .constants import DEFAULT_CHANNEL_MEMBERS, DEFAULT_DIRECT_MEMBERS, DEFAULT_GROUP_MEMBERS
from .value_objects import Name, Permission, Role, RolePriority, RoleType, SystemRole

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
GUEST_PERMISSIONS: Final[set[Permission]] = {
    Permission(code=PermissionCode("message:read"), category="message"),
    Permission(code=PermissionCode("message:react"), category="message"),
}
# Права участника
MEMBER_PERMISSIONS: Final[set[Permission]] = GUEST_PERMISSIONS | {
    Permission(code=PermissionCode("message:send"), category="message"),
    Permission(code=PermissionCode("message:pin"), category="message"),
    Permission(code=PermissionCode("media:send"), category="media"),
    Permission(code=PermissionCode("member:add"), category="member"),
}
# Права админа
ADMIN_PERMISSIONS: Final[set[Permission]] = MEMBER_PERMISSIONS | {
    Permission(code=PermissionCode("member:ban"), category="member"),
    Permission(code=PermissionCode("member:kick"), category="member"),
    Permission(code=PermissionCode("member:mute"), category="member"),
    Permission(code=PermissionCode("member:invite"), category="member"),
}
# Права для владельца ('owner')
OWNER_PERMISSIONS: Final[set[Permission]] = ADMIN_PERMISSIONS | {
    Permission(code=PermissionCode("room:manage"), category="room"),
    Permission(code=PermissionCode("role:manage"), category="role"),
    Permission(code=PermissionCode("role:create"), category="role"),
}

ROLES_REGISTRY: Final[dict[SystemRole, Role]] = {
    SystemRole.GUEST: Role(
        type=RoleType.SYSTEM,
        name=Name("guest"),
        priority=RolePriority(1),
        permissions=list(GUEST_PERMISSIONS),
    ),
    SystemRole.MEMBER: Role(
        type=RoleType.SYSTEM,
        name=Name("member"),
        priority=RolePriority(30),
        permissions=list(MEMBER_PERMISSIONS),
    ),
    SystemRole.ADMIN: Role(
        type=RoleType.SYSTEM,
        name=Name("admin"),
        priority=RolePriority(70),
        permissions=list(ADMIN_PERMISSIONS),
    ),
    SystemRole.OWNER: Role(
        type=RoleType.SYSTEM,
        name=Name("owner"),
        priority=RolePriority(100),
        permissions=list(OWNER_PERMISSIONS),
    )
}
