from typing import Protocol

from abc import abstractmethod

from ..domain.events import EventT


class EventBus(Protocol):
    @abstractmethod
    async def publish(self, event: EventT) -> None: ...
