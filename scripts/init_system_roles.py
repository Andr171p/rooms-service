from uuid import uuid4

ROLES: list[dict[str, str]] = [
    {
        "id": uuid4(),
        "type": "system",
        "name": "owner",
        "description": "Владелец комнаты",
        "priority": 1
    },
    {
        "id": uuid4(),
        "type": "system",
        "name": "admin",
        "description": "Администратор комнаты",
        "priority": 2
    },
    {
        "id": uuid4(),
        "type": "system",
        "name": "moderator",
        "description": "Модератор комнаты",
        "priority": 3
    },
    {
        "id": uuid4(),
        "type": "system",
        "name": "member",
        "description": "Обычный участник",
        "priority": 4
    },
    {
        "id": uuid4(),
        "type": "system",
        "name": "guest",
        "description": "Гость (ограниченные права)",
        "priority": 5
    },
]

PERMISSIONS: list[dict[str, str]] = [
    # Комната
    {"id": uuid4(), "code": "room:edit", "category": "room"},
    {"id": uuid4(), "code": "room:delete", "category": "room"},
    # Настройки комнаты
    {"id": uuid4(), "code": "room_settings:edit", "category": "room_settings"},
    {"id": uuid4(), "code": "room_settings:messages:edit", "category": "room_settings"},
    {"id": uuid4(), "code": "room_settings:members:edit", "category": "room_settings"},
    {"id": uuid4(), "code": "room_settings:media:edit", "category": "room_settings"},
    # Участники
    {"id": uuid4(), "code": "member:invite", "category": "member"},
    {"id": uuid4(), "code": "member:delete", "category": "member"},
    {"id": uuid4(), "code": "member:ban", "category": "member"},
    {"id": uuid4(), "code": "member:change_role", "category": "member"},
    # Сообщения
    {"id": uuid4(), "code": "message:send", "category": "message"},
]
