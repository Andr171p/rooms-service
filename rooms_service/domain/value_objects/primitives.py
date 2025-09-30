from typing import Annotated, Any, Self

import re
from collections import UserString
from collections.abc import Callable
from datetime import datetime
from uuid import UUID, uuid4

from pydantic import Field
from pydantic_core import CoreSchema, core_schema

from ..rules import current_datetime

# Уникальный UUID идентификатор
Id = Annotated[UUID, Field(default_factory=uuid4)]
# Текущее время
CurrentDatetime = Annotated[datetime, Field(default_factory=current_datetime)]


class _IntPrimitiveValidator(int):
    def __new__(cls, value: int, *args, **kwargs) -> Self:
        value = cls.validate(value, *args, **kwargs)
        return super().__new__(cls, value)

    @classmethod
    def validate(cls, value: int, *args, **kwargs) -> int: pass

    @classmethod
    def __get_pydantic_core_schema__(
            cls,
            source_type: Any,
            handler: Callable[[Any], CoreSchema],
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.int_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(int),
        )


class RolePriority(_IntPrimitiveValidator):
    """Тип для валидации приоритета роли"""

    MIN_PRIORITY, MAX_PRIORITY = 1, 100

    @classmethod
    def validate(cls, value: int, *args, **kwargs) -> int:  # noqa: ARG003
        if not (cls.MIN_PRIORITY <= value <= cls.MAX_PRIORITY):
            raise ValueError(
                f"Priority must be between {cls.MIN_PRIORITY} and {cls.MAX_PRIORITY}! "
                f"Invalid value: {value}"
            )
        return value


class _StrPrimitiveValidator(UserString):
    def __init__(self, seq: str) -> None:
        super().__init__(seq)
        self.data = self.validate(self.data)

    @classmethod
    def validate(cls, value: str) -> str: pass

    @classmethod
    def __get_pydantic_core_schema__(
            cls,
            source_type: Any,
            handler: Callable[[Any], CoreSchema],
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(str),
        )


class PermissionCode(_StrPrimitiveValidator):
    """Строка для валидации кода привилегий."""

    MIN_CODE_PARTS = 2

    @classmethod
    def validate(cls, code: str) -> str:
        if ":" not in code:
            raise ValueError(
                """Permission code must contains ':'!
                For example: 'message:send', 'room:create', 'member:delete
                """
            )
        code_parts: list[str] = code.split(":")
        no_empty_code_parts: list[str] = [code_part for code_part in code_parts if code_part]
        if len(no_empty_code_parts) < cls.MIN_CODE_PARTS:
            raise ValueError("Invalid permission code! Not enough no empty parts.")
        return code


class Name(_StrPrimitiveValidator):
    """Строка для валидации имени сущности"""

    MIN_LENGTH, MAX_LENGTH = 1, 100

    @classmethod
    def validate(cls, name: str) -> str:
        if not (cls.MIN_LENGTH <= len(name) <= cls.MAX_LENGTH):
            raise ValueError(
                f"Name length must be between {cls.MIN_LENGTH} and {cls.MAX_LENGTH} characters!"
            )
        return name


class Slug(_StrPrimitiveValidator):
    """Строка для валидации псевдонима сущности"""

    MIN_LENGTH, MAX_LENGTH = 1, 100

    @classmethod
    def validate(cls, slug: str) -> str:
        if not (cls.MIN_LENGTH <= len(slug) <= cls.MAX_LENGTH):
            raise ValueError(
                f"Name length must be between {cls.MIN_LENGTH} and {cls.MAX_LENGTH} characters!"
            )
        return slug.lower()


class CorrelationId(_StrPrimitiveValidator):
    """Id для дебагинга и трассировки между микросервисами.

    Структура correlation_id:
    [название сервиса]--[микросекунды]--[первые 8 символов UUID]
    """

    CORRELATION_ID_PARTS = 3  # Количество составляющих correlation_id.

    @classmethod
    def validate(cls, correlation_id: str) -> str:
        parts: list[str] = correlation_id.split("--")
        if len(parts) != cls.CORRELATION_ID_PARTS:
            raise ValueError("Correlation ID must have 3 parts!")
        second_part = parts[1]
        if not second_part.isdigit():
            raise ValueError("Correlation ID does not contain time of creation in microseconds!")
        if current_datetime().microsecond < int(second_part):
            raise ValueError(
                "Current time cannot be less than the time the correlation id was created!"
            )
        return correlation_id


class EventType(_StrPrimitiveValidator):
    EVENT_TYPE_PARTS = 2

    @classmethod
    def validate(cls, event_type: str) -> str:
        if len(event_type.split("_")) < cls.EVENT_TYPE_PARTS:
            raise ValueError("Event type must have at least two characters!")
        return event_type


class Nickname(_StrPrimitiveValidator):
    """Примитив для никнейма участника комнаты.

     Правила валидации:
         - Длина: от 2 до 32 символов.
         - Допустимые символы: буквы (латиница, кириллица), цифры, подчёркивания, дефисы.
         - Не может состоять только из цифр.
         - Не может содержать пробелы.
         - Тримминг пробелов по краям.
    """
    MIN_LENGTH, MAX_LENGTH = 2, 32
    PATTERN = r"^[a-zA-Za-яА-ЯёЁ0-9_-]+$"
    BANNED_CHARS = "@&"

    @classmethod
    def validate(cls, nickname: str) -> str:
        nickname = nickname.strip()
        if not (cls.MIN_LENGTH <= len(nickname) <= cls.MAX_LENGTH):
            raise ValueError(
                f"Nickname length must be between {cls.MIN_LENGTH} "
                f"and {cls.MAX_LENGTH} characters!"
            )
        if nickname.isdigit():
            raise ValueError("Nickname must not consist only of numbers!")
        for char in nickname:
            if char in cls.BANNED_CHARS:
                raise ValueError(
                    f"Nickname must not contain banned character: '{char}'! "
                    f"Banned characters: '{cls.BANNED_CHARS}'"
                )
        # Проверка допустимых символов:
        if not re.match(cls.PATTERN, nickname):
            raise ValueError(
                "Nickname can only contain letters, numbers, underscores and hyphens!"
            )
        return nickname
