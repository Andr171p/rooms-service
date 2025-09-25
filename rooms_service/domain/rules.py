from datetime import datetime

import pytz

from .value_objects import (
    JoinPermission,
    RoomMediaSettings,
    RoomMembersSettings,
    RoomMessagesSettings,
    RoomSettings,
    RoomType,
    RoomVisibility,
    SystemRole,
)

moscow_tz = pytz.timezone("Europe/Moscow")


def current_datetime() -> datetime:
    """Получает текущее время (учитывает текущий часовой пояс)"""
    return datetime.now(moscow_tz)


# ======================Правила для валидации примитивов======================
MIN_NAME_LENGTH = 1
MAX_NAME_LENGTH = 100

# ======================Правила для комнат======================
# Максимальное количество первичных участников комнаты
MAX_INITIAL_USERS = 50
# Предельные значения числа участников чата (комнаты)
DEFAULT_CHANNEL_MEMBERS = 1_000_000
DEFAULT_GROUP_MEMBERS = 1_000
DEFAULT_DIRECT_MEMBERS = 2
MIN_MEMBERS = 2
MAX_MEMBERS = 10_000_000
MIN_ADMINS = 1
MAX_ADMINS = 50
DEFAULT_ADMINS = 5
# Значения для настроек сообщений в комнате
DEFAULT_PINNED_MESSAGES = 5
MIN_PINNED_MESSAGES = 1
MAX_PINNED_MESSAGES = 100
# Максимальный размер медиа контента в комнате
MIN_MEDIA_SIZE = 50
MAX_MEDIA_SIZE = 1024 * 2
DEFAULT_MEDIA_SIZE = 250
# Разрешённые типы файлов по умолчанию
UNLIMITED_MEDIA_FORMATS: list[str] = ["*"]
ALLOWED_MEDIA_FORMATS: tuple[str, ...] = (
    "jpg", "jpeg", "png", "gif", "mp4", "mov", "pdf", "doc", "docx", "mp3"
)

# ======================Маппинг типа комнаты к её настройкам======================
# Максимальное количество участников в зависимости от типа комнаты
ROOM_TYPE_TO_MAX_MEMBERS_MAP: dict[RoomType, int] = {
    RoomType.DIRECT: DEFAULT_DIRECT_MEMBERS,
    RoomType.CHANNEL: DEFAULT_CHANNEL_MEMBERS,
    RoomType.GROUP: DEFAULT_GROUP_MEMBERS,
}
# Дефолтная роль пользователя в зависимости от типа комнаты
ROOM_TYPE_TO_SYSTEM_ROLE_MAP: dict[RoomType, SystemRole] = {
    RoomType.DIRECT: SystemRole.MEMBER,
    RoomType.GROUP: SystemRole.MEMBER,
    RoomType.CHANNEL: SystemRole.GUEST,
}


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
            max_members=ROOM_TYPE_TO_MAX_MEMBERS_MAP[room_type],
            join_permission=join_permission
        ),
        media=RoomMediaSettings(),
    )
