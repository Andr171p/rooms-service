from uuid import uuid4

SYSTEM_ROLES: list[dict[str, str]] = [
    {
        "id": uuid4(),
        "type": "system",
        "name": "owner",
        "description": "Владелец комнаты",
        "priority": 100
    },
    {
        "id": uuid4(),
        "type": "system",
        "name": "admin",
        "description": "Администратор комнаты",
        "priority": 80
    },
    {
        "id": uuid4(),
        "type": "system",
        "name": "moderator",
        "description": "Модератор комнаты",
        "priority": 60
    },
    {
        "id": uuid4(),
        "type": "system",
        "name": "member",
        "description": "Обычный участник",
        "priority": 50
    },
    {
        "id": uuid4(),
        "type": "system",
        "name": "guest",
        "description": "Гость (ограниченные права)",
        "priority": 30
    },
]

PERMISSIONS: list[dict[str, str]] = [
    # Комната
    {"code": "room:edit", "category": "room"},
    {"code": "room:delete", "category": "room"},
    # Настройки комнаты
    {"code": "room_settings:edit", "category": "room_settings"},
    {"code": "room_settings:messages:edit", "category": "room_settings"},
    {"code": "room_settings:members:edit", "category": "room_settings"},
    {"code": "room_settings:media:edit", "category": "room_settings"},
    # Участники
    {"code": "member:invite", "category": "member"},
    {"code": "member:delete", "category": "member"},
    {"code": "member:ban", "category": "member"},
    {"code": "member:change_role", "category": "member"},
    # Сообщения
    {"code": "message:send", "category": "message"},
    {"code": "message:edit", "category": "message"},
    {"code": "message:delete", "category": "message"},
    {"code": "message:pin", "category": "message"},
]
