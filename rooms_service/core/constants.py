from .enums import RoomType

# Самый высокий приоритет роли
HIGHEST_PRIORITY = 1
# Предельные значения числа участников группового чата
DEFAULT_CHANNEL_MEMBERS = 10_000_000
DEFAULT_GROUP_MEMBERS = 1_000
DEFAULT_DIRECT_MEMBERS = 2
MIN_MEMBERS = 2
MAX_MEMBERS = 10_000_000
# Значения для настроек сообщений
DEFAULT_PINNED_MESSAGES = 5
MIN_PINNED_MESSAGES = 1
MAX_PINNED_MESSAGES = 100
# Разрешённые типы файлов по умолчанию
ALL_ALLOWED_MEDIA_FORMATS: list[str] = ["*"]
ALLOWED_MEDIA_FORMATS: list[str] = [
    "jpg", "jpeg", "png", "gif", "mp4", "mov", "pdf", "doc", "docx", "mp3"
]
# Максимальное количество участников в зависимости от типа комнаты
TYPE_TO_MAX_MEMBERS_MAPPING: dict[RoomType, int] = {
    RoomType.DIRECT: DEFAULT_DIRECT_MEMBERS,
    RoomType.CHANNEL: DEFAULT_CHANNEL_MEMBERS,
    RoomType.GROUP: DEFAULT_GROUP_MEMBERS,
}
