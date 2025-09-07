from typing import Protocol, Self, TypeVar

from abc import ABC, abstractmethod
from uuid import UUID

from pydantic import BaseModel

from .domain import Member, Room

SchemaT = TypeVar("SchemaT", bound=BaseModel)


class Command(ABC, BaseModel):
    """Абстрактный класс для создания команды"""


class Query(ABC, BaseModel):
    """Абстрактный класс для создания запроса"""


class CommandHandler[ResultT: BaseModel](ABC):
    @abstractmethod
    async def handle(self, command: Command, **kwargs) -> ResultT: pass


class CRUDRepository[SchemaT: BaseModel](Protocol):
    async def create(self, schema: SchemaT) -> SchemaT:
        """Создаёт ресурс и возвращает его"""

    async def read(self, id: UUID) -> SchemaT | None:  # noqa: A002
        """Получает ресурс по его уникальному идентификатору"""

    async def update(self, id: UUID, **kwargs) -> SchemaT | None:  # noqa: A002
        """Обновляет ресурс"""

    async def delete(self, id: UUID) -> bool:  # noqa: A002
        """Удаляет ресурс"""


class MemberRepository(CRUDRepository[Member]):
    async def bulk_create(self, members: list[Member]) -> list[Member]:
        """Создаёт за одну операцию множество ресурсов"""


class UnitOfWork(ABC):
    """Реализация Unit Of Work паттерна для атомарности согласованности данных"""

    room_repository: type[CRUDRepository[Room]]
    member_repository: type[MemberRepository]

    @abstractmethod
    async def __aenter__(self) -> Self: pass

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()

    @abstractmethod
    async def commit(self) -> None: pass

    @abstractmethod
    async def rollback(self) -> None: pass
