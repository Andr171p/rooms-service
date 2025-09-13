from typing import Any

from collections.abc import Mapping, Sequence
from uuid import UUID

from pydantic import PositiveInt
from sqlalchemy import Index, delete, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Mapped

from ..core.base import OutboxRepository
from ..core.constants import EventStatus
from ..core.events import OutboxEvent
from ..core.exceptions import DeletionError, ReadingError
from .base import Base, JsonDict, PostgresUUID
from .repository import SQLCRUDRepository


class OutboxEventModel(Base):
    __tablename__ = "outbox_events"

    event_id: Mapped[PostgresUUID, UUID]
    aggregate_type: Mapped[str]
    aggregate_id: Mapped[PostgresUUID]
    event_type: Mapped[str]
    payload: Mapped[JsonDict]
    event_status: Mapped[str]
    retries: Mapped[int]
    dedup_key: Mapped[str]
    partition_key: Mapped[str]

    __table_args__ = (
        Index("outbox_index", "status", "aggregate_id", "dedup_key", "partition_key"),
    )


class SQLOutboxRepository(SQLCRUDRepository[OutboxEventModel, OutboxEvent], OutboxRepository):
    model = OutboxEventModel
    schema = OutboxEvent

    async def get_count_by_status(self, event_statuses: Sequence[EventStatus]) -> int:
        try:
            stmt = select(func.count()).where(self.model.event_status.in_(event_statuses))
            result = await self.session.execute(stmt)
            return result.scalar()
        except SQLAlchemyError as e:
            raise ReadingError(
                f"Error while reading events count with {event_statuses} status: {e}"
            ) from e

    async def get_by_status(
            self, event_statuses: Sequence[EventStatus], limit: PositiveInt, page: PositiveInt
    ) -> list[OutboxEvent]:
        try:
            offset = (page - 1) * limit
            stmt = (
                select(self.model)
                .where(self.model.event_status.in_(event_statuses))
                .order_by(self.model.created_at)
                .offset(offset)
                .limit(limit)
            )
            results = await self.session.execute(stmt)
            models = results.scalars().all()
            return [self.schema.model_validate(model) for model in models]
        except SQLAlchemyError as e:
            raise ReadingError(f"Error while reading data: {e}") from e

    async def bulk_update(self, ids: list[UUID], *args: list[Mapping[str, Any]]) -> None:
        pass

    async def bulk_delete(self, ids: list[UUID]) -> None:
        try:
            stmt = delete(self.model).where(self.model.id.in_(ids))
            await self.session.execute(stmt)
            await self.session.commit()
        except SQLAlchemyError as e:
            raise DeletionError(f"Error while deleting data: {e}") from e
