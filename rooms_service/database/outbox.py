from sqlalchemy import Index
from sqlalchemy.orm import Mapped

from .base import Base, JsonDict, PostgresUUID


class OutboxEventModel(Base):
    __tablename__ = "outbox_events"

    aggregate_type: Mapped[str]
    aggregate_id: Mapped[PostgresUUID]
    event_type: Mapped[str]
    payload: Mapped[JsonDict]
    status: Mapped[str]
    retries: Mapped[int]
    dedup_key: Mapped[str]
    partition_key: Mapped[str]

    __table_args__ = (
        Index("outbox_index", "status", "aggregate_id", "dedup_key", "partition_key"),
    )
