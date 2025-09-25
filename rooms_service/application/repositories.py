from __future__ import annotations

from typing import Protocol, Self, TypeVar

from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from uuid import UUID

from pydantic import BaseModel, PositiveInt

from ..domain.aggragates import RoomRole
from ..domain.entities import Member, Room
from ..domain.value_objects import MemberIdentity
from .dto import MemberCreate

EntityT = TypeVar("EntityT", bound=BaseModel)


class UnitOfWork(ABC):
    """Абстрактный класс для реализации Unit Of Work паттерна,
     обеспечивающий атомарность и согласованность данных.
    """
    room_repository: RoomRepository
    member_repository: MemberRepository

    @abstractmethod
    async def __aenter__(self) -> Self:
        pass

    @abstractmethod
    @asynccontextmanager
    async def transaction(self) -> Self: pass

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()

    @abstractmethod
    async def commit(self) -> None:
        pass

    @abstractmethod
    async def rollback(self) -> None:
        pass


class GenericCRUDRepository(Protocol[EntityT]):
    async def create(self, entity: EntityT) -> EntityT:
        """Создание сущности"""

    @abstractmethod
    async def read(self, id: UUID) -> EntityT | None:  # noqa: A002
        """Получает сущность по её уникальному идентификатору"""

    @abstractmethod
    async def update(self, id: UUID, **kwargs) -> EntityT | None:  # noqa: A002
        """Обновляет состояние сущности"""

    @abstractmethod
    async def delete(self, id: UUID) -> bool:  # noqa: A002
        """Удаляет сущность"""


class RoomRepository(GenericCRUDRepository[Room]):
    @abstractmethod
    async def get_members(self, id: UUID, limit: PositiveInt, page: PositiveInt) -> list[Member]:  # noqa: A002
        """Получает участников комнаты"""


class MemberRepository(GenericCRUDRepository[Member]):
    async def create(self, member: MemberCreate | Member) -> Member:
        """Переопределения создания сущности участника"""

    @abstractmethod
    async def bulk_create(self, members: list[MemberCreate]) -> list[Member]:
        """Создание множества участников за раз"""

    @abstractmethod
    async def get_by_identity(self, identity: MemberIdentity) -> Member | None:
        """Получает участника по его уникальной комбинации атрибутов"""

    @abstractmethod
    async def get_room_role(self, id: UUID) -> RoomRole:  # noqa: A002
        """Получает роль участника по его id"""
