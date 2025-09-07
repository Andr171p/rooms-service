from typing import TypeVar

from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.domain import Room
from ..core.exceptions import (
    ConflictError,
    CreationError,
    DeletionError,
    ReadingError,
    UpdateError,
)
from .base import Base
from .models import RoomModel

ModelT = TypeVar("ModelT", bound=Base)
SchemaT = TypeVar("SchemaT", bound=BaseModel)


class CRUDRepository[ModelT: Base, SchemaT: BaseModel]:
    model: type[ModelT]
    schema: type[SchemaT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, schema: SchemaT) -> SchemaT:
        try:
            stmt = insert(self.model).values(**schema.model_dump()).returning(self.model)
            result = await self.session.execute(stmt)
            await self.session.commit()
            created_model = result.scalar_one()
            return self.schema.model_validate(created_model)
        except IntegrityError as e:
            await self.session.rollback()
            raise ConflictError(f"Data conflict error: {e}") from e
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise CreationError(f"Error while creation: {e}") from e

    async def read(self, id: UUID) -> SchemaT | None:  # noqa: A002
        try:
            stmt = select(self.model).where(self.model.id == id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            return self.schema.model_validate(model) if model else None
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ReadingError(f"Error while reading: {e}") from e

    async def read_all(self, limit: int, page: int) -> list[SchemaT]:
        try:
            offset = (page - 1) * limit
            stmt = select(self.model).offset(offset).limit(limit)
            results = await self.session.execute(stmt)
            models = results.scalars().all()
            return [self.schema.model_validate(model) for model in models]
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ReadingError(f"Error while reading: {e}") from e

    async def update(self, id: UUID, **kwargs) -> SchemaT | None:  # noqa: A002
        try:
            stmt = (
                update(self.model)
                .values(**kwargs)
                .where(self.model.id == id)
                .returning(self.model)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            updated_model = result.scalar_one_or_none()
            return self.schema.model_validate(updated_model) if updated_model else None
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise UpdateError(f"Error while update: {e}") from e

    async def delete(self, id: UUID) -> bool:  # noqa: A002
        try:
            stmt = delete(self.model).where(self.model.id == id)
            result = await self.session.execute(stmt)
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DeletionError(f"Error while deletion: {e}") from e
        else:
            return result.rowcount > 0


class RoomRepository(CRUDRepository[RoomModel, Room]):
    model = RoomModel
    schema = Room

    async def create(self, room: Room) -> Room:
        try:
            model = RoomModel(**room.model_dump())
            self.session.add(model)
            await self.session.commit()
            await self.session.refresh(model, ["settings"])
            return Room.model_validate(model)
        except IntegrityError as e:
            await self.session.rollback()
            raise ConflictError(f"Data conflict error: {e}") from e
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise CreationError(f"Error while creation: {e}") from e
