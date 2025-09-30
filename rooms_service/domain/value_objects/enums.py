from enum import StrEnum


class EventStatus(StrEnum):
    """Статусы жизненного цикла события"""
    NEW = "new"
    PENDING = "pending"
    DONE = "done"
    FAILED = "failed"


class RoomType(StrEnum):
    """Тип комнаты (чата)"""
    DIRECT = "direct"  # Личный чат one to one
    GROUP = "group"  # Групповой чат
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
    MUTED = "muted"  # Не может писать и взаимодействовать с сообщениями
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


class MemberPermissionStatus(StrEnum):
    """Статус права для участника"""
    GRANT = "grant"
    DENY = "deny"
