from __future__ import annotations

from typing import Protocol, Self, TypeVar

from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from uuid import UUID

from pydantic import BaseModel, PositiveInt

from ..domain.aggragates import Room
from ..domain.entities import Member
from ..domain.value_objects import Role
from .dto import MemberAdd, RoomCreate

EntityT = TypeVar("EntityT", bound=BaseModel)


class UnitOfWork(ABC):
    """Абстрактный класс для реализации Unit Of Work паттерна,
     обеспечивающий атомарность и согласованность данных.
    """
    room_repository: RoomRepository

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


class ReadableRepository(Protocol[EntityT]):
    @abstractmethod
    async def read(self, id: UUID) -> EntityT | None: pass  # noqa: A002

    @abstractmethod
    async def read_all(self, limit: PositiveInt, page: PositiveInt) -> list[EntityT]: pass


class CRUDRepository(ReadableRepository[EntityT], Protocol[EntityT]):
    @abstractmethod
    async def create(self, entity: EntityT) -> EntityT: pass

    @abstractmethod
    async def update(self, id: UUID, **kwargs) -> EntityT | None: pass  # noqa: A002

    @abstractmethod
    async def delete(self, id: UUID) -> bool: pass  # noqa: A002


class RoomRepository(ReadableRepository[Room]):
    @abstractmethod
    async def create(self, room: RoomCreate) -> Room:
        """Создаёт комнату"""

    @abstractmethod
    async def add_members(self, members: list[MemberAdd]) -> None:
        """Массовое добавление участников"""

    @abstractmethod
    async def add_role(self, role: Role) -> Role:
        """Добавляет кастомную роль для комнаты"""

    @abstractmethod
    async def get_members(self, id: UUID, limit: PositiveInt, page: PositiveInt) -> list[Member]:  # noqa: A002
        """Получает участников комнаты"""
