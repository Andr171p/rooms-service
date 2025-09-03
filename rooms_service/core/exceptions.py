class _RepositoryError(Exception):
    """Базовая ошибка репозитория"""


class MismatchError(_RepositoryError):
    """Ошибка при несоответствии данных"""


class CreationError(_RepositoryError):
    """Ошибка при создании ресурса"""


class AlreadyExistsError(_RepositoryError):
    """Ресурс уже создан"""


class ReadingError(_RepositoryError):
    """Ошибка при чтении данных"""


class UpdateError(_RepositoryError):
    """Ошибка обновления данных"""


class DeletionError(_RepositoryError):
    """Ошибка удаления данных"""
