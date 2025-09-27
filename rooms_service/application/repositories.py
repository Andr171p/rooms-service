from __future__ import annotations

from typing import Protocol, Self, TypeVar

from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from uuid import UUID

from pydantic import BaseModel, PositiveInt

from ..domain.aggragates import RoomRole
from ..domain.entities import Member, Role, Room
from ..domain.value_objects import MemberIdentity, Name
from .dto import MemberCreate

EntityT = TypeVar("EntityT", bound=BaseModel)


class UnitOfWork(ABC):
    """Абстрактный класс для реализации Unit Of Work паттерна,
     обеспечивающий атомарность и согласованность данных.
    """
    room_repository: RoomRepository
    role_repository: RoleRepository
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


class ReadableRepository(Protocol[EntityT]):
    async def read(self, id: UUID) -> EntityT | None: pass  # noqa: A002

    async def read_all(self, limit: PositiveInt, page: PositiveInt) -> list[EntityT]: pass


class CRUDRepository(ReadableRepository[EntityT], Protocol[EntityT]):
    async def create(self, entity: EntityT) -> EntityT: pass

    async def update(self, id: UUID, **kwargs) -> EntityT | None: pass  # noqa: A002

    async def delete(self, id: UUID) -> bool: pass  # noqa: A002


class RoomRepository(CRUDRepository[Room]):
    @abstractmethod
    async def get_members(self, id: UUID, limit: PositiveInt, page: PositiveInt) -> list[Member]:  # noqa: A002
        """Получает участников комнаты"""


class RoleRepository(CRUDRepository[Role]):
    async def get_by_name(self, name: Name) -> Role | None:
        """Получает роль по её уникальному имени"""


class MemberRepository(Protocol):
    @abstractmethod
    async def create(self, member: MemberCreate) -> Member:
        """Переопределения создания сущности участника"""

    @abstractmethod
    async def bulk_create(self, members: list[MemberCreate]) -> list[Member]:
        """Создание множества участников за раз"""

    @abstractmethod
    async def read(self, id: UUID) -> Member | None:  # noqa: A002
        """Чтение участника из ресурса по его идентификатору"""

    @abstractmethod
    async def update(self, id: UUID, **kwargs) -> Member | None: pass  # noqa: A002

    @abstractmethod
    async def delete(self, id: UUID) -> bool: pass  # noqa: A002

    @abstractmethod
    async def get_by_identity(self, identity: MemberIdentity) -> Member | None:
        """Получает участника по его уникальной комбинации атрибутов"""

    @abstractmethod
    async def get_room_role(self, id: UUID) -> RoomRole:  # noqa: A002
        """Получает роль участника по его id"""
