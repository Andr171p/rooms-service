from uuid import UUID

from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ...application.dto import RoomCreate
from ...domain.aggragates import Room
from ...domain.exceptions import ConflictError, CreationError
from ...domain.value_objects import Name, Role, RoleType
from ..models import MemberModel, RoleModel, RoomModel, RoomRoleModel


class SQLRoomCreateRepository:
    session: "AsyncSession"

    async def create(self, room: RoomCreate) -> Room:
        try:
            stmt = (
                insert(RoomModel)
                .values(**room_created.model_dump(exclude={"members"}))
                .returning(RoomModel)
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one()
            roles: set[Role] = set()
            room_roles = await self._create_room_roles(model.id, roles)
            members: list[MemberModel] = [
                MemberModel(
                    id=member.id,
                    room_id=member.room_id,
                    room_role_id=room_roles[member.role],
                    status=member.status,
                    joined_at=member.joined_at,
                )
                for member in room_created.members
            ]
            self.session.add_all(members)
            return Room.model_validate(model)
        except IntegrityError as e:
            raise ConflictError(
                f"Room already exists with id: {room_created.id}, error: {e}"
            ) from e
        except SQLAlchemyError as e:
            raise CreationError(f"Error occurred while room creation, error: {e}") from e

    async def _find_role(self, name: Name, type: RoleType) -> RoleModel | None:  # noqa: A002
        stmt = select(RoleModel).where((RoleModel.name == name) & (RoleModel.type == type))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def _create_room_roles(self, room_id: UUID, roles: set[Role]) -> dict[Role, UUID]:
        room_roles: dict[Role, UUID] = {}
        for role in roles:
            role_model = await self._find_role(role.name, role.type)
            stmt = (
                insert(RoomRoleModel)
                .values(room_id=room_id, role_id=role_model.id)
                .returning(RoomRoleModel)
            )
            result = await self.session.execute(stmt)
            room_role_model = result.scalar_one()
            room_roles[role] = room_role_model.id
        return room_roles
