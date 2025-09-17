import logging
from datetime import timedelta
from uuid import UUID

from faststream.exceptions import FastStreamException

from .core.base import OutboxRepository, Publisher
from .core.constants import EventStatus
from .core.utils import schedule, total_pages

# Задержка в секундах между операциями outbox процессора
OUTBOX_PROCESSOR_SLEEP = 5
# Интервал между отчистками failed событий (раз в час)
OUTBOX_CLEANUP_SLEEP = 3600
# Количество обрабатываемых outbox событий за раз
OUTBOX_PROCESSOR_BATCH_SIZE = 32
# Статусы которые обрабатывает Outbox Processor
OUTBOX_PROCESSOR_STATUSES: tuple[EventStatus, ...] = (EventStatus.NEW, EventStatus.PENDING)
# Статусы для удаления
OUTBOX_CLEANUP_STATUSES: tuple[EventStatus, ...] = (EventStatus.FAILED,)

logger = logging.getLogger(__name__)


class OutboxProcessor:
    """Обработчик Outbox событий"""
    def __init__(
            self, repository: OutboxRepository, publisher: Publisher
    ) -> None:
        self.repository = repository
        self.publisher = publisher

    @schedule(timedelta(seconds=OUTBOX_PROCESSOR_SLEEP))
    async def process(self) -> None:
        count = await self.repository.get_count_by_status(OUTBOX_PROCESSOR_STATUSES)
        pages = total_pages(count, OUTBOX_PROCESSOR_BATCH_SIZE)
        if pages == 0:
            return
        for page in range(1, pages + 1):
            outbox_events = await self.repository.get_by_status(
                OUTBOX_PROCESSOR_STATUSES, page=page, limit=OUTBOX_PROCESSOR_BATCH_SIZE
            )
            event_ids: list[UUID] = [outbox_event.event_id for outbox_event in outbox_events]
            try:
                await self.publisher.publish(
                    [outbox_event.payload for outbox_event in outbox_events]
                )
                await self.repository.bulk_delete(event_ids)
            except FastStreamException:
                logger.exception("Error while processing outbox events, error: {e}")
                statuses = [{"event_status": EventStatus.PENDING} for _ in range(len(event_ids))]
                await self.repository.bulk_update(event_ids, statuses)


class OutboxCleaner:
    """Worker для удаления просроченных outbox событий"""
    def __init__(self, repository: OutboxRepository) -> None:
        self.repository = repository

    @schedule(timedelta(seconds=OUTBOX_CLEANUP_SLEEP))
    async def cleanup(self) -> None:
        count = await self.repository.get_count_by_status(OUTBOX_CLEANUP_STATUSES)
        pages = total_pages(count, OUTBOX_PROCESSOR_BATCH_SIZE)
        if pages == 0:
            return
        for page in range(1, pages + 1):
            outbox_events = await self.repository.get_by_status(
                OUTBOX_CLEANUP_STATUSES, page=page, limit=OUTBOX_PROCESSOR_BATCH_SIZE
            )
            await self.repository.bulk_delete([
                outbox_event.event_id for outbox_event in outbox_events
            ])
            logger.info("%s outbox events ware successfully cleaned", len(outbox_events))
