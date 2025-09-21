from typing import TypeVar

from uuid import UUID

from pydantic import BaseModel, PositiveInt
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.base import MemberRepository, RoleRepository, RoomRepository
from ..core.constants import MemberPermissionStatus
from ..core.domain import Member, Permission, Role, Room
from ..core.dto import RolePermission
from ..core.exceptions import (
    ConflictError,
    CreationError,
    DeletionError,
    ReadingError,
    UpdateError,
)
from .base import Base
from .models import (
    MemberModel,
    MemberPermissionModel,
    PermissionModel,
    RoleModel,
    RolePermissionModel,
    RoomModel,
    RoomRoleModel,
)

ModelT = TypeVar("ModelT", bound=Base)
SchemaT = TypeVar("SchemaT", bound=BaseModel)


class SQLCRUDRepository[ModelT: Base, SchemaT: BaseModel]:
    model: type[ModelT]
    schema: type[SchemaT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, schema: SchemaT) -> SchemaT:
        try:
            stmt = insert(self.model).values(**schema.model_dump()).returning(self.model)
            result = await self.session.execute(stmt)
            created_model = result.scalar_one()
            return self.schema.model_validate(created_model)
        except IntegrityError as e:
            raise ConflictError(f"Data conflict error: {e}") from e
        except SQLAlchemyError as e:
            raise CreationError(f"Error while creation: {e}") from e

    async def read(self, id: UUID) -> SchemaT | None:  # noqa: A002
        try:
            stmt = select(self.model).where(self.model.id == id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            return self.schema.model_validate(model) if model else None
        except SQLAlchemyError as e:
            raise ReadingError(f"Error while reading: {e}") from e

    async def read_all(self, limit: PositiveInt, page: PositiveInt) -> list[SchemaT]:
        try:
            offset = (page - 1) * limit
            stmt = select(self.model).offset(offset).limit(limit)
            results = await self.session.execute(stmt)
            models = results.scalars().all()
            return [self.schema.model_validate(model) for model in models]
        except SQLAlchemyError as e:
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
            updated_model = result.scalar_one_or_none()
            return self.schema.model_validate(updated_model) if updated_model else None
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


class SQLRoomRepository(SQLCRUDRepository[RoomModel, Room], RoomRepository):
    model = RoomModel
    schema = Room

    async def create(self, room: Room) -> Room:
        try:
            model = RoomModel(**room.model_dump())
            self.session.add(model)
            await self.session.refresh(model, ["settings"])
            return Room.model_validate(model)
        except IntegrityError as e:
            await self.session.rollback()
            raise ConflictError(f"Data conflict error: {e}") from e
        except SQLAlchemyError as e:
            raise CreationError(f"Error while creation: {e}") from e

    async def get_members(
            self, id: UUID, page: PositiveInt, limit: PositiveInt  # noqa: A002
    ) -> list[Member]:
        try:
            offset = (page - 1) * limit
            stmt = (
                select(MemberRepository)
                .where(MemberModel.room_id == id)
                .offset(offset)
                .limit(limit)
            )
            results = await self.session.execute(stmt)
            models = results.scalars().all()
            return [Member.model_validate(model) for model in models]
        except SQLAlchemyError as e:
            raise ReadingError(f"Error while reading: {e}") from e

    async def get_roles(self, id: UUID) -> list[Role]:
        try:
            stmt = (
                select(RoleModel)
                .join(RoomRoleModel, RoomRoleModel.room_id == id)
                .where(RoomRoleModel.role_id == RoleModel.id)
            )
            results = await self.session.execute(stmt)
            models = results.scalars().all()
            return [Role.model_validate(model) for model in models]
        except SQLAlchemyError as e:
            raise ReadingError(f"Error while reading: {e}") from e

    async def get_role_permissions(self, id: UUID) -> list[RolePermission]:  # noqa: A002
        try:
            stmt = (
                select(RoleModel.id, RoleModel.name, PermissionModel.code)
                .join(RoomRoleModel, RoomRoleModel.role_id == RoleModel.id)
                .join(RolePermissionModel, RolePermissionModel.role_id == RoleModel.id)
                .join(PermissionModel, RolePermissionModel.permission_code == PermissionModel.code)
                .where(RoomRoleModel.room_id == id)
                .order_by(PermissionModel.code)
            )
            results = await self.session.execute(stmt)
            role_permissions: list[RolePermission] = []
            for role_id, role_name, permission_code in results.all():
                role_permissions.append(RolePermission(
                    role_id=role_id, role_name=role_name, permission_code=permission_code
                ))
            return role_permissions
        except SQLAlchemyError as e:
            raise ReadingError(f"Error while reading: {e}") from e


class SQLMemberRepository(SQLCRUDRepository[MemberModel, Member], MemberRepository):
    model = MemberModel
    schema = Member

    async def bulk_create(self, members: list[Member]) -> None:
        try:
            values = [member.model_dump() for member in members]
            stmt = insert(self.model).values(**values)
            await self.session.execute(stmt)
        except IntegrityError as e:
            raise ConflictError(f"Data conflict error: {e}") from e
        except SQLAlchemyError as e:
            raise CreationError(f"Error while creation: {e}") from e

    async def get_by_room_and_user(self, room_id: UUID, user_id: UUID) -> Member | None:
        try:
            stmt = (
                select(self.model)
                .where(
                    (self.model.room_id == room_id) &
                    (self.model.user_id == user_id)
                )
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            return self.schema.model_validate(model) if model else None
        except SQLAlchemyError as e:
            raise ReadingError(f"Error while reading: {e}") from e

    async def get_permissions(self, id: UUID) -> list[Permission]:  # noqa: A002
        try:
            stmt = (
                select(PermissionModel)
                .join(MemberPermissionModel)
                .where(
                    (MemberPermissionModel.member_id == id) &
                    MemberPermissionModel.status == MemberPermissionStatus.GRANT
                )
            )
            results = await self.session.execute(stmt)
            models = results.scalars().all()
            return [Permission.model_validate(model) for model in models]
        except SQLAlchemyError as e:
            raise ReadingError(f"Error while reading: {e}") from e


class SQLRoleRepository(SQLCRUDRepository[RoleModel, Role], RoleRepository):
    model = RoleModel
    schema = Role

    async def get_by_name(self, name: str) -> Role | None:
        try:
            stmt = select(self.model).where(self.model.name == name)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            return self.schema.model_validate(model) if model else None
        except SQLAlchemyError as e:
            raise ReadingError(f"Error while reading: {e}") from e

    async def get_permissions(self, role_id: UUID) -> list[Permission]:
        try:
            stmt = (
                select(PermissionModel)
                .join(
                    RolePermissionModel,
                    RolePermissionModel.permission_code == PermissionModel.code,
                )
                .where(RolePermissionModel.role_id == role_id)
            )
            result = await self.session.execute(stmt)
            models = result.scalars().all()
            return [Permission.model_validate(model) for model in models]
        except SQLAlchemyError as e:
            raise ReadingError(f"Error while reading: {e}") from e
