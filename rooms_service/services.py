import logging
from datetime import timedelta
from uuid import UUID

from .core.base import OutboxRepository, Publisher
from .core.constants import (
    OUTBOX_PROCESSOR_BATCH_SIZE,
    OUTBOX_PROCESSOR_SLEEP,
    OUTBOX_PROCESSOR_STATUSES,
    EventStatus,
)
from .core.utils import schedule, total_pages

logger = logging.getLogger(__name__)


class OutboxProcessor:
    """Обработчик Outbox событий"""
    def __init__(
            self, repository: OutboxRepository, publisher: Publisher
    ) -> None:
        self.repository = repository
        self.publisher = publisher

    @schedule(timedelta(seconds=OUTBOX_PROCESSOR_SLEEP))
    async def process(self) -> ...:
        count = await self.repository.get_count_by_status(OUTBOX_PROCESSOR_STATUSES)
        pages = total_pages(count, OUTBOX_PROCESSOR_BATCH_SIZE)
        if pages == 0:
            ...
        for page in range(1, pages + 1):
            outbox_events = await self.repository.get_by_status(
                OUTBOX_PROCESSOR_STATUSES, page=page, limit=OUTBOX_PROCESSOR_BATCH_SIZE
            )
            ids: list[UUID] = [outbox_event.event_id for outbox_event in outbox_events]
            try:
                await self.publisher.publish(
                    [outbox_event.payload for outbox_event in outbox_events]
                )
                await self.repository.bulk_delete(ids)
            except Exception:
                logger.exception("Error while processing outbox events, error: {e}")
                statuses = [{"event_status": EventStatus.PENDING} for _ in range(len(ids))]
                await self.repository.bulk_update(ids, statuses)
