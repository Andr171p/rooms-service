from typing import TypeVar

from uuid import UUID

from pydantic import BaseModel, PositiveInt
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ...application.repositories import CRUDRepository
from ...domain.entities import Role
from ...domain.exceptions import (
    ConflictError,
    CreationError,
    DeletionError,
    ReadingError,
    UpdateError,
)
from ..base import Base
from ..models import RoleModel

ModelT = TypeVar("ModelT", bound=Base)
EntityT = TypeVar("EntityT", bound=BaseModel)


class SQLReadableRepository[ModelT: Base, EntityT: BaseModel]:
    model: type[ModelT]
    entity: type[EntityT]

    session: "AsyncSession"

    async def read(self, id: UUID) -> EntityT | None:  # noqa: A002
        try:
            stmt = select(self.model).where(self.model.id == id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            return self.entity.model_validate(model) if model else None
        except SQLAlchemyError as e:
            raise ReadingError(
                f"Error occurred while {self.entity.__name__.lower()} reading by id {id}, "
                f"error: {e}"
            ) from e

    async def read_all(self, limit: PositiveInt, page: PositiveInt) -> list[EntityT]:
        try:
            offset = (page - 1) * limit
            stmt = select(self.model).offset(offset).limit(limit)
            results = await self.session.execute(stmt)
            models = results.scalars().all()
            return [self.entity.model_validate(model) for model in models]
        except SQLAlchemyError as e:
            raise ReadingError(
                f"Error occurred while reading all {self.entity.__name__.lower()}s "
                f"by limit {limit}, page {page}, error: {e}"
            ) from e


class SQLCRUDRepository[ModelT: Base, EntityT: BaseModel](SQLReadableRepository[ModelT, EntityT]):
    model: type[ModelT]
    entity: type[EntityT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, entity: EntityT) -> EntityT:
        try:
            stmt = insert(self.model).values(**entity.model_dump()).returning(self.model)
            result = await self.session.execute(stmt)
            created_model = result.scalar_one()
            return self.entity.model_validate(created_model)
        except IntegrityError as e:
            raise ConflictError(
                f"Creation of {self.entity.__name__.lower()} failed due data conflict error: {e}"
            ) from e
        except SQLAlchemyError as e:
            raise CreationError(
                f"Error occurred while {self.entity.__name__.lower()} creation, error: {e}"
            ) from e

    async def update(self, id: UUID, **kwargs) -> EntityT | None:  # noqa: A002
        try:
            stmt = (
                update(self.model)
                .values(**kwargs)
                .where(self.model.id == id)
                .returning(self.model)
            )
            result = await self.session.execute(stmt)
            updated_model = result.scalar_one_or_none()
            return self.entity.model_validate(updated_model) if updated_model else None
        except SQLAlchemyError as e:
            raise UpdateError(
                f"Error occurred while {self.entity.__name__.lower()} update by id {id}, "
                f"error: {e}"
            ) from e

    async def delete(self, id: UUID) -> bool:  # noqa: A002
        try:
            stmt = delete(self.model).where(self.model.id == id)
            result = await self.session.execute(stmt)
        except SQLAlchemyError as e:
            raise DeletionError(
                f"Error occurred while {self.entity.__name__} deletion by id {id}, "
                f"error: {e}"
            ) from e
        else:
            return result.rowcount > 0


class SQLRoleRepository(SQLCRUDRepository[RoleModel, Role], CRUDRepository[Role]):
    model = RoleModel
    entity = Role
