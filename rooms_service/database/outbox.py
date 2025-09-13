from pydantic import PositiveInt
from sqlalchemy import Index, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Mapped

from ..core.base import OutboxRepository
from ..core.constants import EventStatus
from ..core.events import OutboxEvent
from ..core.exceptions import ReadingError
from .base import Base, JsonDict, PostgresUUID
from .repository import SQLCRUDRepository


class OutboxEventModel(Base):
    __tablename__ = "outbox_events"

    aggregate_type: Mapped[str]
    aggregate_id: Mapped[PostgresUUID]
    type: Mapped[str]
    payload: Mapped[JsonDict]
    status: Mapped[str]
    retries: Mapped[int]
    dedup_key: Mapped[str]
    partition_key: Mapped[str]

    __table_args__ = (
        Index("outbox_index", "status", "aggregate_id", "dedup_key", "partition_key"),
    )


class SQLOutboxRepository(SQLCRUDRepository[OutboxEventModel, OutboxEvent], OutboxRepository):
    model = OutboxEventModel
    schema = OutboxEvent

    async def get_by_status(
            self, status: EventStatus, limit: PositiveInt, page: PositiveInt
    ) -> list[OutboxEvent]:
        try:
            offset = (page - 1) * limit
            stmt = (
                select(self.model)
                .where(self.model.status == status)
                .order_by(self.model.created_at)
                .offset(offset)
                .limit(limit)
            )
            results = await self.session.execute(stmt)
            models = results.scalars().all()
            return [self.schema.model_validate(model) for model in models]
        except SQLAlchemyError as e:
            raise ReadingError(f"Error while reading data: {e}") from e
