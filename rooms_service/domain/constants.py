# ======================Конфигурация микро-сервиса======================
SOURCE = "rooms-service"
# ======================Приоритеты системных ролей======================
GUEST_PRIORITY = 1
MEMBER_PRIORITY = 30
ADMIN_PRIORITY = 70
OWNER_PRIORITY = 100
# ======================Правила для комнат======================
# Максимальное количество первичных участников комнаты
MAX_INITIAL_USERS = 50
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
ALLOWED_MEDIA_FORMATS: tuple[str, ...] = (
    "jpg", "jpeg", "png", "gif", "mp4", "mov", "pdf", "doc", "docx", "mp3"
)
# ======================Outbox значения======================
# Максимальное количество повторных обработок для outbox процессора
MAX_OUTBOX_RETRIES = 5
# ======================Прочие сервисные константы======================
# Время жизни ресурса в кеше
TTL = 3600
