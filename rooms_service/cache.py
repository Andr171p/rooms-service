import logging
from datetime import timedelta
from uuid import UUID

from pydantic import BaseModel
from redis.asyncio import Redis
from redis.exceptions import RedisError

from .core.constants import TTL
from .core.exceptions import CreationError, DeletionError, ReadingError

logger = logging.getLogger(__name__)


class RedisCRUDRepository[SchemaT: BaseModel]:
    schema: type[SchemaT]
    class_name = SchemaT.__class__.__name__

    def __init__(
            self, redis: Redis, prefix: str, ttl: timedelta | int = TTL
    ) -> None:
        self.redis = redis
        self.prefix = prefix
        self.ttl = ttl

    def _build_key(self, identifier: str | UUID) -> str:
        """Составляет уникальный ключ объекта

        :param identifier: Идентификатор объекта.
        :return: Уникальный ключ объекта в кеше.
        """
        return f"{self.prefix}:{identifier}"

    async def create(self, schema: SchemaT) -> SchemaT:
        try:
            key = self._build_key(schema.id)
            await self.redis.set(key, schema.model_dump_json(exclude_none=True))
            await self.redis.expire(key, TTL)
        except RedisError as e:
            logger.exception(
                "Error while creation %s, error: {e}", self.class_name
            )
            raise CreationError(f"Error while creation {self.class_name}") from e
        else:
            return schema

    async def read(self, id: UUID) -> SchemaT | None:  # noqa: A002
        try:
            key = self._build_key(id)
            result = await self.redis.get(key)
            if result is None:
                return None
            json_result = result.decode("utf-8")
            return self.schema.model_validate_json(json_result)
        except RedisError as e:
            logger.exception(
                "Error while reading %s, error: {e}", self.class_name
            )
            raise ReadingError("Error while reading %s", self.class_name) from e

    async def update(self, id: UUID, **kwargs) -> SchemaT:  # noqa: A002
        ...

    async def delete(self, id: UUID) -> bool:  # noqa: A002
        try:
            key = self._build_key(id)
            is_deleted = await self.redis.delete(key)
        except RedisError as e:
            logger.exception(
                "Error while deletion %s, error: {e}", self.class_name
            )
            raise DeletionError(f"Error while deletion {self.class_name}") from e
        else:
            return is_deleted > 0
