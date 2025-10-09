from collections.abc import Sequence
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
        """Создание комнаты вместе с ролями, правами и участниками в рамках одной транзакции.

        :param room: DTO для создания комнаты.
        :return Агрегат созданной комнаты.
        """
        try:
            model = RoomModel(**room.model_dump(exclude={"roles"}))
            self.session.add(model)
            room_roles_map = await self.__create_room_roles(room.id, room.roles)
            await self.__save_members(room.members, room_roles_map)
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

    async def __create_room_roles(self, room_id: UUID, roles: list[Role]) -> dict[Name, UUID]:
        """Создаёт роли внутри комнаты с правами. Записывает данные в таблицу 'room_roles'
        и 'room_role_permissions' (внутри метода используется метод __add_room_role_permissions)

        :param room_id: Комната в которую нужно добавить роли.
        :param roles: Роли, которые нужно добавить.
        :return Маппинг role_name -> room_role_id.
        :raise ValueError - если не существует запрашиваемой системной роли.
        """
        system_role_names: set[Name] = {
            role.name for role in roles if role.type == RoleType.SYSTEM
        }
        system_role_models = await self._find_system_roles(system_role_names)
        system_roles_map: dict[Name, UUID] = {
            system_role_model.name: system_role_model.id
            for system_role_model in system_role_models
        }
        room_roles_map: dict[Name, UUID] = {}
        for role in set(roles):
            system_role_id = system_roles_map.get(role.name)
            if role.type == RoleType.SYSTEM and system_role_id is None:
                raise ValueError(f"System role '{role.name}' does not exist!")
            stmt = (
                insert(RoomRoleModel)
                .values(
                    room_id=room_id,
                    role_id=system_role_id,
                    name=role.name,
                    priority=role.priority,
                    is_default=role.is_default,
                )
                .returning(RoomRoleModel)
            )
            result = await self.session.execute(stmt)
            room_role_model = result.scalar_one()
            await self.__add_room_role_permissions(room_role_model.id, role.permissions)
            room_roles_map[role.name] = room_role_model.id
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

    async def _find_system_roles(self, role_names: set[Name]) -> Sequence[RoleModel]:
        """Находит системные роль по последовательности уникальных имён.

        :param role_names: Уникальные имена ролей.
        :return SQLAlchemy модели ролей.
        """
        stmt = select(RoleModel).where(RoleModel.name.in_(role_names))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def __save_members(
            self, members: list[MemberAdd], room_roles_map: dict[Name, UUID]
    ) -> None:
        """Сохраняет участников в комнату.

        :param members: DTO участников для добавления.
        :param room_roles_map: Маппинг role_name и их room_role_id.
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

    async def _find_room_roles(
            self, room_id: UUID, role_names: set[Name]
    ) -> Sequence[RoomRoleModel]:
        """Находит роли внутри комнаты по последовательности уникальных имён ролей.
        Выполняет поиск за один запрос по совпадению role_names.
        ПРИМЕЧАНИЕ: количество найденных ролей может быть меньше количества room_roles, т.к
        роль с таким room_roles могла быть не создана.

        :param room_id: Комната в которой нужно найти роли.
        :param role_names: Уникальная последовательность имён ролей.
        :return Найденные роли внутри комнаты.
        """
        stmt = (
            select(RoomRoleModel)
            .where(
                (RoomRoleModel.room_id == room_id) &
                (RoomRoleModel.name.in_(role_names))
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def add_members(self, members: list[MemberAdd]) -> None:
        """Добавляет участников в комнату.

        :param members: DTO для добавления участников.
        :raise ValueError:
             - При пустом списке участников.
             - Комнатная роль не найдена.
        """
        if not members:
            raise ValueError("Empty members list!")
        try:
            room_id = members[0].room_id
            if any(member.room_id != room_id for member in members):
                raise ValueError("All members must belong to the same room!")
            role_names: set[Name] = {member.role_name for member in members}
            room_role_models = await self._find_room_roles(room_id, role_names)
            room_roles_map: dict[Name, UUID] = {
                Name(room_role_model.name): room_role_model.id
                for room_role_model in room_role_models
            }
            missing_roles = role_names - room_roles_map.keys()
            if missing_roles:
                raise ValueError(
                    f"Roles not found in room {room_id}: {missing_roles}!"
                )
            await self.__save_members(members, room_roles_map)
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise CreationError(f"Error occurred while adding members, error: {e}") from e
