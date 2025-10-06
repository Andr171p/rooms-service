from uuid import UUID

from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ...application.dto import MemberAdd, RoomCreate
from ...application.exceptions import ConflictError, CreationError
from ...domain.aggragates import Room
from ...domain.value_objects import Name, Permission, Role, RoleType
from ..models import (
    MemberModel,
    PermissionModel,
    RoleModel,
    RoomModel,
    RoomRoleModel,
    RoomRolePermissionModel,
)


class SQLRoomCreatableRepository:
    session: "AsyncSession"

    async def create(self, room: RoomCreate) -> Room:
        """Создание комнаты вместе с ролями, правами и участниками.
        Атомарная операция.

        :param room: DTO для создания комнаты.
        :return Агрегат созданной комнаты.
        """
        try:
            model = RoomModel(**room.model_dump(exclude={"roles"}))
            self.session.add(model)
            await self.__create_roles(room.id, room.roles)
            await self.session.flush()
            await self.session.commit()
            return Room.model_validate({**model.to_dict, "roles": room.roles})
        except IntegrityError as e:
            await self.session.rollback()
            raise ConflictError(
                f"Room already exists with id: {room.id}, error: {e}"
            ) from e
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise CreationError(f"Error occurred while room creation, error: {e}") from e

    async def __create_roles(self, room_id: UUID, roles: list[Role]) -> dict[Name, UUID]:
        """Создаёт роли внутри комнаты с правами.

        :param room_id: Комната в которую нужно добавить роли.
        :param roles: Роли, которые нужно добавить.
        :return Маппинг role_name -> room_role_id.
        :raise ValueError - если не существует запрашиваемой системной роли.
        """
        room_roles_map: dict[Name, UUID] = {}
        for role in set(roles):
            system_role: RoleModel | None = None
            if role.type == RoleType.SYSTEM:
                system_role = await self._find_system_role(role.name)
                if system_role is None:
                    raise ValueError(f"System role '{role.name}' does not exist!")
            stmt = (
                insert(RoomRoleModel)
                .values(
                    room_id=room_id,
                    role_id=system_role.id if system_role else None,
                    name=role.name,
                    priority=role.priority,
                    is_default=role.is_default,
                )
                .returning(RoomRoleModel)
            )
            result = await self.session.execute(stmt)
            room_role = result.scalar_one()
            await self.__add_room_role_permissions(room_role.id, role.permissions)
            room_roles_map[role.name] = room_role.id
        return room_roles_map

    async def __add_room_role_permissions(
            self, room_role_id: UUID, permissions: list[Permission]
    ) -> None:
        """Добавляет права для роли внутри комнаты.
        Находит права по их уникальному коду, после чего реализует маппинг
        ролей и прав внутри комнаты (создаёт записи в таблице 'room_role_permissions').

        :param room_role_id: Идентификатор роли внутри комнаты.
        :param permissions: Список прав для роли.
        :raise ValueError - если запрашиваемые права не соответствуют найденным.
        """
        stmt = (
            select(PermissionModel)
            .where(PermissionModel.code.in_({permission.code for permission in permissions}))
        )
        results = await self.session.execute(stmt)
        permission_models = results.scalars().all()
        if len(permission_models) != len(set(permissions)):
            missing_permissions = (
                    {permission.code for permission in permissions} -
                    {permission_model.code for permission_model in permission_models}
            )
            raise ValueError(f"Permissions not found! Missing permissions: {missing_permissions}")
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

    async def __add_members(
            self, members: list[MemberAdd], room_roles_map: dict[Name, UUID]
    ) -> None:
        """Добавляет участников в комнату.

        :param members: DTO участников для добавления.
        :param room_roles_map: Маппинг названий ролей и их room_role_id.
        """
        models = [
            MemberModel(
                id=member.id,
                user_id=member.user_id,
                room_role_id=room_roles_map[member.role_name],
                status=member.status,
                joined_at=member.joined_at,
            )
            for member in members
        ]
        self.session.add_all(models)

    async def _get_room_role(self, room_id: UUID, role_name: Name) -> RoomRoleModel | None:
        stmt = (
            select(RoomRoleModel)
            .where(
                (RoomRoleModel.room_id == room_id) &
                (RoomRoleModel.name == role_name)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def add_members(self, members: list[MemberAdd]) -> None:
        try:
            room_role_model = await self._get_room_role(members[0].room_id, members[0].role_name)
            if room_role_model is None:
                raise ValueError(
                    f"Role {members[0].role_name} not found in room {members[0].room_id}!"
                )
            models: list[MemberModel] = [
                MemberModel(
                    id=member.id,
                    user_id=member.user_id,
                    room_id=member.room_id,
                    room_role_id=room_role_model.id,
                    status=member.status,
                    joined_at=member.joined_at,
                )
                for member in members
            ]
            self.session.add_all(models)
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise CreationError(f"Error occurred while adding members, error: {e}") from e
