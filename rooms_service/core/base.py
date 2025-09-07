from typing import TypeVar

from abc import ABC, abstractmethod

from pydantic import BaseModel

ResultT = TypeVar("ResultT", bound=BaseModel)


class Command(ABC, BaseModel):
    """Абстрактный класс для создания команды"""


class Query(ABC, BaseModel):
    """Абстрактный класс для создания запроса"""


class CommandHandler[ResultT: BaseModel](ABC):
    @abstractmethod
    async def handle(self, command: Command, **kwargs) -> ResultT:
        raise NotImplementedError
