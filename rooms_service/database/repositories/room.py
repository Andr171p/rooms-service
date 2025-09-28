from uuid import UUID

from pydantic import PositiveInt
from sqlalchemy import insert, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ...application.dto import RoomCreate
from ...application.repositories import RoomRepository
from ...domain.aggragates import RoomRole
from ...domain.entities import Member, Permission, Role, Room
from ...domain.exceptions import CreationError, ReadingError
from ...domain.value_objects import Name
from ..models import MemberModel, RoleModel, RolePermissionModel, RoomModel, RoomRoleModel
from .crud import SQLReadableRepository


class SQLRoomRepository(SQLReadableRepository[RoomModel, Room], RoomRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, room: RoomCreate) -> Room:
        try:
            stmt = insert(RoomModel).values(**room.model_dump()).returning(RoomModel)
            result = await self.session.execute(stmt)
            model = result.scalar_one()
            return Room.model_validate(model)
        except SQLAlchemyError as e:
            raise CreationError(f"Error occurred while creation room, error: {e}") from e

    async def get_members(
            self, id: UUID, limit: PositiveInt, page: PositiveInt  # noqa: A002
    ) -> list[Member]:
        try:
            offset = (page - 1) * limit
            stmt = (
                select(MemberModel)
                .options(joinedload(MemberModel.role))
                .where(MemberModel.room_id == id)
                .offset(offset)
                .limit(limit)
            )
            results = await self.session.execute(stmt)
            models = results.scalars().all()
            return [Member.model_validate(model) for model in models]
        except SQLAlchemyError as e:
            raise ReadingError(
                f"Error occurred while reading members in room with {id}, error: {e}"
            ) from e

    async def get_role(self, id: UUID, role_name: Name) -> RoomRole | None:  # noqa: A002
        try:
            stmt = (
                select(RoomRoleModel)
                .join(RoomRoleModel.role)
                .join(RoleModel.role_permissions)
                .join(RolePermissionModel.permission)
                .options(
                    joinedload(RoomRoleModel.role)
                    .joinedload(RoleModel.role_permissions)
                    .joinedload(RolePermissionModel.permission)
                )
                .where(
                    (RoomRoleModel.room_id == id) &
                    (RoleModel.name == role_name)
                )
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is None:
                return None
            return self._convert_to_room_role_from_model(model)
        except SQLAlchemyError as e:
            raise ReadingError(
                f"Error occurred while reading room role in room with id {id}, "
                f"role name: {role_name}, error: {e}"
            ) from e

    async def get_roles(self, id: UUID) -> list[RoomRole]:  # noqa: A002
        try:
            stmt = (
                select(RoomRoleModel)
                .join(RoomRoleModel.role)
                .join(RoleModel.role_permissions)
                .join(RolePermissionModel.permission)
                .options(
                    joinedload(RoomRoleModel.role)
                    .joinedload(RoleModel.role_permissions)
                    .joinedload(RolePermissionModel.permission)
                )
                .where(RoomRoleModel.room_id == id)
            )
            results = await self.session.execute(stmt)
            models = results.scalars().all()
            return [self._convert_to_room_role_from_model(model) for model in models]
        except SQLAlchemyError as e:
            raise ReadingError(
                f"Error occurred while reading room roles in room with id {id}, error: {e}"
            ) from e

    @staticmethod
    def _convert_to_room_role_from_model(model: RoomRoleModel) -> RoomRole:
        room_id = model.room_id
        role = Role.model_validate(model.role)
        permissions: list[Permission] = [
            Permission.model_validate(role_permission.permission)
            for role_permission in model.role.role_permissions
        ]
        return RoomRole(room_id=room_id, role=role, permissions=permissions)
