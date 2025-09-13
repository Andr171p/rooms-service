from enum import StrEnum

# Параметры для валидации имён
MIN_NAME_LENGTH = 1
MAX_NAME_LENGTH = 100
# Самый высокий приоритет роли
HIGHEST_PRIORITY = 1
# Количество частей в коде привилегий
PERMISSION_CODE_PARTS = 2
# Предельные значения числа участников группового чата
DEFAULT_CHANNEL_MEMBERS = 1_000_000
DEFAULT_GROUP_MEMBERS = 1_000
DEFAULT_DIRECT_MEMBERS = 2
MIN_MEMBERS = 2
MAX_MEMBERS = 10_000_000
MIN_ADMINS = 1
MAX_ADMINS = 50
DEFAULT_ADMINS = 5
# Значения для настроек сообщений
DEFAULT_PINNED_MESSAGES = 5
MIN_PINNED_MESSAGES = 1
MAX_PINNED_MESSAGES = 100
# Максимальный размер медиа контента в комнате
MIN_MEDIA_SIZE = 50
MAX_MEDIA_SIZE = 1024 * 2
DEFAULT_MEDIA_SIZE = 250
# Разрешённые типы файлов по умолчанию
UNLIMITED_MEDIA_FORMATS: list[str] = ["*"]
ALLOWED_MEDIA_FORMATS: list[str] = [
    "jpg", "jpeg", "png", "gif", "mp4", "mov", "pdf", "doc", "docx", "mp3"
]
# Максимальное количество повторных обработок для outbox процессора
MAX_OUTBOX_RETRIES = 5
# Задержка в секундах между операциями outbox процессора
OUTBOX_PROCESSOR_SLEEP = 5
# Количество обрабатываемых outbox событий за раз
OUTBOX_PROCESSOR_BATCH_SIZE = 32


class EventStatus(StrEnum):
    """Статусы жизненного цикла события"""
    NEW = "new"
    PENDING = "pending"
    DONE = "done"
    FAILED = "failed"


# Статусы которые обрабатывает Outbox Processor
OUTBOX_PROCESSOR_STATUSES: tuple[EventStatus, ...] = (EventStatus.NEW, EventStatus.PENDING)


class RoomType(StrEnum):
    """Тип комнаты (чата)"""
    DIRECT = "direct"    # Личный чат one to one
    GROUP = "group"      # Групповой чат
    CHANNEL = "channel"  # Канал: новости, блог и.т.д


class RoomVisibility(StrEnum):
    """Видимость комнаты для других пользователей"""
    PRIVATE = "private"
    PUBLIC = "public"
    DELETED = "deleted"
    BANNED = "banned"


class MemberStatus(StrEnum):
    """Статус участника"""
    ACTIVE = "active"  # Может полноценно использовать разрешённый ему функционал
    MUTED = "muted"    # Не может писать и взаимодействовать с сообщениями
    BANNED = "banned"  # Не может ни взаимодействовать, ни читать контент


class SystemRole(StrEnum):
    """Системные роли участника комнаты"""
    OWNER = "owner"          # Владелец комнаты, самые высокие привилегии
    ADMIN = "admin"          # Администратор, может управлять участниками + привилегии модератора
    MODERATOR = "moderator"  # Модератор, может удалять и управлять сообщениями
    MEMBER = "member"        # Участник, может взаимодействовать с сообщениями
    GUEST = "guest"          # Гость
    READER = "reader"        # Читатель, может только просматривать сообщения
    BOT = "bot"              # Бот


class RoleType(StrEnum):
    """Тип роли участника"""
    SYSTEM = "system"  # Системная роль, не подлежит изменениям
    CUSTOM = "custom"  # Роль, которую может создать пользователь


class MediaType(StrEnum):
    """Возможные типы медиа контента"""
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    AUDIO = "audio"
    STICKER = "sticker"


class JoinPermission(StrEnum):
    """Правила присоединения новых участников"""
    OPEN = "open"
    APPROVAL = "approval"
    INVITE_ONLY = "invite_only"


class InvitationStatus(StrEnum):
    """Статус отправленного приглашения в комнату"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


# Максимальное количество участников в зависимости от типа комнаты
TYPE_TO_MAX_MEMBERS_MAP: dict[RoomType, int] = {
    RoomType.DIRECT: DEFAULT_DIRECT_MEMBERS,
    RoomType.CHANNEL: DEFAULT_CHANNEL_MEMBERS,
    RoomType.GROUP: DEFAULT_GROUP_MEMBERS,
}
# Дефолтная роль пользователя в зависимости от типа комнаты
TYPE_TO_SYSTEM_ROLE_MAP: dict[RoomType, SystemRole] = {
    RoomType.DIRECT: SystemRole.MEMBER,
    RoomType.GROUP: SystemRole.MEMBER,
    RoomType.CHANNEL: SystemRole.GUEST,
}
