from uuid import UUID

from sqlalchemy import case, delete, insert, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ...application.dto import MemberCreate
from ...application.repositories import MemberRepository
from ...core.exceptions import (
    ConflictError,
    CreationError,
    DeletionError,
    ReadingError,
    UpdateError,
)
from ...domain.aggragates import RoomRole
from ...domain.entities import Member, Permission, Role
from ...domain.value_objects import MemberIdentity, PermissionCode
from ..models import MemberModel, PermissionModel, RoleModel, RolePermissionModel


class SQLMemberRepository(MemberRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _load_role(self, role_id: UUID) -> Role:
        stmt = select(RoleModel).where(RoleModel.id == role_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            raise ValueError(f"Role with id {role_id} does not exist!")
        return Role.model_validate(model) if model else None

    async def _bulk_load_roles(self, role_ids: list[UUID]) -> list[Role]:
        order_case = case(
            *[(RoleModel.id == role_id, i) for i, role_id in enumerate(role_ids)],
            else_=len(role_ids)
        )
        stmt = select(RoleModel).where(RoleModel.id.in_(role_ids)).order_by(order_case)
        results = await self.session.execute(stmt)
        models = results.scalars().all()
        return [Role.model_validate(model) for model in models]

    async def create(self, member: Member | MemberCreate) -> Member:
        try:
            if isinstance(member, MemberCreate):
                stmt = insert(MemberModel).values(**member.model_dump()).returning(MemberModel)
            else:
                stmt = (
                    insert(MemberModel)
                    .values(**member.model_dump(exclude={"role"}), role_id=member.role.id)
                    .returning(MemberModel)
                )
            result = await self.session.execute(stmt)
            model = result.scalar_one()
            role = await self._load_role(member.role.id)
            return Member.model_validate(model.to_dict.update({"role": role}))
        except IntegrityError as e:
            raise ConflictError(f"Creation of member failed due data conflict error: {e}") from e
        except SQLAlchemyError as e:
            raise CreationError(f"Error occurred while member creation, error: {e}") from e

    async def bulk_create(self, members: list[MemberCreate]) -> list[Member]:
        stmt = (
            insert(MemberModel)
            .values([member.model_dump() for member in members])
            .returning(MemberModel)
        )
        results = await self.session.execute(stmt)
        models = results.scalars().all()
        roles = await self._bulk_load_roles([model.role_id for model in models])
        return [
            Member.model_validate(model.to_dict.update({"role": role}))
            for model, role in zip(models, roles, strict=False)
        ]

    async def read(self, id: UUID) -> Member | None:  # noqa: A002
        try:
            stmt = select(MemberModel).where(MemberModel.id == id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is None:
                return None
            role = await self._load_role(model.role.id)
            return Member.model_validate(model.to_dict.update({"role": role}))
        except SQLAlchemyError as e:
            raise ReadingError(
                f"Error occurred while member reading by id {id}, error: {e}"
            ) from e

    async def update(self, id: UUID, **kwargs) -> Member | None:  # noqa: A002
        try:
            stmt = (
                update(MemberModel)
                .values(**kwargs)
                .where(MemberModel.id == id)
                .returning(MemberModel)
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is None:
                return None
            role = await self._load_role(model.role.id)
            return Member.model_validate(model.to_dict.update({"role": role}))
        except SQLAlchemyError as e:
            raise UpdateError(
                f"Error occurred while member updating by id {id}, error: {e}"
            ) from e

    async def delete(self, id: UUID) -> bool:  # noqa: A002
        try:
            stmt = delete(MemberModel).where(MemberModel.id == id)
            result = await self.session.execute(stmt)
        except SQLAlchemyError as e:
            raise DeletionError(
                f"Error occurred while member deleting by id {id}, error: {e}"
            ) from e
        else:
            return result.rowcount > 0

    async def get_by_identity(self, identity: MemberIdentity) -> Member | None:
        try:
            stmt = (
                select(MemberModel)
                .where(
                    (MemberModel.user_id == identity.user_id) &
                    (MemberModel.room_id == identity.room_id)
                )
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is None:
                return None
            role = await self._load_role(model.role.id)
            return Member.model_validate(model.to_dict.update({"role": role}))
        except SQLAlchemyError as e:
            raise ReadingError(
                f"Error occurred while receipt "
                f"by identity user_id {identity.user_id}, room_id {identity.room_id}, "
                f"error: {e}"
            ) from e

    async def get_room_role(self, id: UUID) -> RoomRole:  # noqa: A002
        try:
            stmt = (
                select(
                    MemberModel.room_id,
                    RoleModel,
                    PermissionModel,
                )
                .select_from(MemberModel)
                .join(MemberModel.role)
                .join(RoleModel.role_permissions)
                .join(RolePermissionModel.permission)
                .where(MemberModel.id == id)
            )
            result = await self.session.execute(stmt)
            rows = result.all()
            if not rows:
                raise ValueError(f"Member with id {id} not found!")
            first_row = rows[0]
            room_id: UUID = first_row.room_id
            role_model: RoleModel = first_row.RoleModel
            permissions_set: set[tuple[UUID, PermissionCode, str]] = set()
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
