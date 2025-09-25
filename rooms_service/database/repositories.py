from typing import TypeVar, override

from uuid import UUID

from pydantic import BaseModel, PositiveInt
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ..application.dto import MemberCreate
from ..application.repositories import MemberRepository
from ..core.exceptions import (
    ConflictError,
    CreationError,
    DeletionError,
    ReadingError,
    UpdateError,
)
from ..domain.aggragates import RoomRole
from ..domain.entities import Member, Permission, Role
from ..domain.value_objects import PermissionCode
from .base import Base
from .models import MemberModel, PermissionModel, RoleModel, RolePermissionModel

ModelT = TypeVar("ModelT", bound=Base)
EntityT = TypeVar("EntityT", bound=BaseModel)


class SQLGenericCRUDRepository[ModelT: Base, EntityT: BaseModel]:
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
            raise ConflictError(f"Data conflict error: {e}") from e
        except SQLAlchemyError as e:
            raise CreationError(f"Error while creation: {e}") from e

    async def read(self, id: UUID) -> EntityT | None:  # noqa: A002
        try:
            stmt = select(self.model).where(self.model.id == id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            return self.entity.model_validate(model) if model else None
        except SQLAlchemyError as e:
            raise ReadingError(f"Error while reading: {e}") from e

    async def read_all(self, limit: PositiveInt, page: PositiveInt) -> list[EntityT]:
        try:
            offset = (page - 1) * limit
            stmt = select(self.model).offset(offset).limit(limit)
            results = await self.session.execute(stmt)
            models = results.scalars().all()
            return [self.entity.model_validate(model) for model in models]
        except SQLAlchemyError as e:
            raise ReadingError(f"Error while reading: {e}") from e

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
            raise UpdateError(f"Error while update: {e}") from e

    async def delete(self, id: UUID) -> bool:  # noqa: A002
        try:
            stmt = delete(self.model).where(self.model.id == id)
            result = await self.session.execute(stmt)
        except SQLAlchemyError as e:
            raise DeletionError(f"Error while deletion: {e}") from e
        else:
            return result.rowcount > 0


class SQLMemberRepository(SQLGenericCRUDRepository[MemberModel, Member], MemberRepository):
    model = MemberModel
    entity = Member

    async def _get_role(self, role_id: UUID) -> Role | None:
        stmt = select(RoleModel).where(self.model.id == role_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return Role.model_validate(model) if model else None

    @override
    async def create(self, member: Member | MemberCreate) -> Member:
        try:
            if isinstance(member, MemberCreate):
                stmt = insert(self.model).values(**member.model_dump()).returning(self.model)
            else:
                stmt = (
                    insert(self.model)
                    .values(**member.model_dump(exclude={"role"}), role_id=member.role.id)
                    .returning(self.model)
                )
            result = await self.session.execute(stmt)
            model = result.scalar_one()
            role = await self._get_role(member.role.id)
            if role is None:
                raise ValueError(f"Role with id {member.role.id} does not exist!")
            return self.entity.model_validate(model.to_dict.update({"role": role}))
        except IntegrityError as e:
            ...
        except SQLAlchemyError as e:
            ...

    async def get_room_role(self, id: UUID) -> RoomRole:  # noqa: A002
        try:
            stmt = (
                select(
                    self.model.room_id,
                    RoleModel,
                    PermissionModel,
                )
                .select_from(self.model)
                .join(self.model.role)
                .join(RoleModel.role_permissions)
                .join(RolePermissionModel.permission)
                .where(self.model.id == id)
            )
            result = await self.session.execute(stmt)
            rows = result.all()
            if not rows:
                raise ValueError(f"Member with id {id} not found!")
            first_row = rows[0]
            room_id: UUID = first_row.room_id
            role_model: RoleModel = first_row.RoleModel
            permissions_set = set()
            for row in rows:
                permission_model = row.PermissionModel
                permissions_set.add((
                    permission_model.id,
                    PermissionCode(permission_model.code),
                    permission_model.category
                ))
            role = Role.model_validate(role_model)
            permissions = [
                Permission(id=id, code=code, category=category)
                for id, code, category in permissions_set  # noqa: A001
            ]
            return RoomRole(room_id=room_id, role=role, permissions=permissions)
        except SQLAlchemyError as e:
            raise ReadingError(f"Error while reading: {e}") from e
