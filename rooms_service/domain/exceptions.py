class _DomainError(Exception):
    """Доменная ошибка"""


class MembersExceededError(_DomainError):
    """Превышено максимальное число пользователей"""
