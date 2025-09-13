from typing import Any, Protocol, Self, TypeVar

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from contextlib import asynccontextmanager
from uuid import UUID

from pydantic import BaseModel, PositiveInt

from .constants import EventStatus
from .domain import Member, Permission, Role, Room
from .events import OutboxEvent
from .value_objects import MessagePayload

SchemaT = TypeVar("SchemaT", bound=BaseModel)


class Command(ABC, BaseModel):
    """Абстрактный класс для создания команды"""


class Query(ABC, BaseModel):
    """Абстрактный класс для создания запроса"""


class CommandHandler[ResultT: BaseModel](ABC):
    """Абстрактный обработчик команд для CQRS паттерна.
    Параметр ResultT указывает возвращаемый объект после обработки команды.
    """

    @abstractmethod
    async def handle(self, command: Command, **kwargs) -> ResultT: pass


class CRUDRepository(Protocol[SchemaT]):
    @abstractmethod
    async def create(self, schema: SchemaT) -> SchemaT:
        """Создаёт ресурс и возвращает его"""

    @abstractmethod
    async def read(self, id: UUID) -> SchemaT | None:  # noqa: A002
        """Получает ресурс по его уникальному идентификатору"""

    @abstractmethod
    async def read_all(self, limit: PositiveInt, page: PositiveInt) -> list[SchemaT]:
        """Выполняет пагинацию ресурса"""

    @abstractmethod
    async def update(self, id: UUID, **kwargs) -> SchemaT | None:  # noqa: A002
        """Обновляет ресурс"""

    async def delete(self, id: UUID) -> bool:  # noqa: A002
        """Удаляет ресурс"""


class RoomRepository(CRUDRepository[Room]):
    @abstractmethod
    async def get_members(
            self, id: UUID, page: PositiveInt, limit: PositiveInt  # noqa: A002
    ) -> list[Member]:
        """Получает всех участников комнаты"""


class MemberRepository(CRUDRepository[Member]):
    @abstractmethod
    async def bulk_create(self, members: list[Member]) -> None:
        """Создаёт за одну операцию множество ресурсов"""


class RoleRepository(CRUDRepository[Role]):
    @abstractmethod
    async def get_by_name(self, name: str) -> Role | None:
        """Получает роль по её названию"""

    @abstractmethod
    async def get_permissions(self, role_id: UUID) -> list[Permission]:
        """Получает права выданные для роли в рамках комнаты"""


class OutboxRepository(CRUDRepository[OutboxEvent]):
    @abstractmethod
    async def get_count_by_status(self, event_statuses: Sequence[EventStatus]) -> int:
        """Получает количество outbox событий с заданным статусом"""

    @abstractmethod
    async def get_by_status(
            self, event_statuses: Sequence[EventStatus], limit: PositiveInt, page: PositiveInt
    ) -> list[OutboxEvent]:
        """Получает события по заданному статусу"""

    @abstractmethod
    async def bulk_update(self, ids: list[UUID], *args: list[Mapping[str, Any]]) -> None:
        """Выполняет обновление N количества ресурсов за раз"""

    @abstractmethod
    async def bulk_delete(self, ids: list[UUID]) -> None:
        """Удаляет N outbox ивентов за один раз.
        Данный метод самостоятельно делает commit изменений без помощи UnitOfWork.
        """


class UnitOfWork(ABC):
    """Абстрактный класс для реализации Unit Of Work паттерна
    для атомарности согласованности данных
    """

    room_repository: RoomRepository
    member_repository: MemberRepository
    role_repository: RoleRepository
    outbox_repository: OutboxRepository

    @abstractmethod
    async def __aenter__(self) -> Self: pass

    @abstractmethod
    @asynccontextmanager
    async def transaction(self) -> Self: pass

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()

    @abstractmethod
    async def commit(self) -> None: pass

    @abstractmethod
    async def rollback(self) -> None: pass


class Publisher(Protocol):
    async def publish(self, message: MessagePayload, **kwargs) -> None:
        """Публикует событие"""
