from uuid import UUID

from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ...application.dto import RoomCreate
from ...domain.aggragates import Room
from ...domain.exceptions import ConflictError, CreationError
from ...domain.value_objects import Name, Permission, Role, RoleType
from ..models import (
    PermissionModel,
    RoleModel,
    RoomRoleModel,
    RoomRolePermissionModel,
)


class SQLRoomCreateRepository:
    session: "AsyncSession"

    async def create(self, room: RoomCreate) -> Room:
        try:
            self.session.add(**room.model_dump(exclude={"roles", "members"}))
            return Room.model_validate(...)
        except IntegrityError as e:
            raise ConflictError(
                f"Room already exists with id: {room.id}, error: {e}"
            ) from e
        except SQLAlchemyError as e:
            raise CreationError(f"Error occurred while room creation, error: {e}") from e

    async def _create_roles(self, room_id: UUID, roles: list[Role]) -> ...:
        """Создаёт роли внутри комнаты с правами.

        :param room_id: Комната в которую нужно добавить роли.
        :param roles: Роли, которые нужно добавить.
        """
        for role in set(roles):
            if role.type == RoleType.SYSTEM:
                system_role = await self._find_system_role(role.name)
                if system_role is None:
                    raise ValueError(f"System role {role.name} does not exist!")
                stmt = (
                    insert(RoomRoleModel)
                    .values(
                        room_id=room_id,
                        role_id=system_role.id,
                        name=role.name,
                        priority=role.priority,
                        is_default=role.is_default,
                    )
                    .returning(RoomRoleModel)
                )
                result = await self.session.execute(stmt)
                room_role = result.scalar_one()
        return ...

    async def _add_room_role_permissions(
            self, room_role_id: UUID, permissions: list[Permission]
    ) -> None:
        """Добавляет права для роли внутри комнаты.
        Находит права по их уникальному коду

        :param room_role_id: Идентификатор роли внутри комнаты.
        :param permissions: Список прав для роли.
        """
        stmt = (
            select(PermissionModel)
            .where(PermissionModel.code.in_({permission.code for permission in permissions}))
        )
        results = await self.session.execute(stmt)
        permission_models = results.scalars().all()
        if permission_models:
            stmt = insert(RoomRolePermissionModel)
            values = [
                {"room_role_id": room_role_id, "permission_id": permission_model.id}
                for permission_model in permission_models
            ]
            await self.session.execute(stmt, values)

    async def _find_system_role(self, name: Name) -> RoleModel | None:
        """Находит системную роль по её уникальному имени.

        :param name: Уникальное имя роли.
        :return SQLAlchemy модель роли.
        """
        stmt = select(RoleModel).where(RoleModel.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
