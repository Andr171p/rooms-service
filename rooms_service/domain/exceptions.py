class _DomainError(Exception):
    """Доменная ошибка"""


class MembersExceededError(_DomainError):
    """Превышено максимальное число пользователей"""


class _RepositoryError(Exception):
    """Базовая ошибка репозитория"""


class MismatchError(_RepositoryError):
    """Ошибка при несоответствии данных"""


class CreationError(_RepositoryError):
    """Ошибка при создании ресурса"""


class ConflictError(_RepositoryError):
    """Конфликт при создании ресурса"""


class ReadingError(_RepositoryError):
    """Ошибка при чтении данных"""


class UpdateError(_RepositoryError):
    """Ошибка обновления данных"""


class DeletionError(_RepositoryError):
    """Ошибка удаления данных"""
