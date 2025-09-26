from uuid import UUID

from sqlalchemy import case, delete, insert, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

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
from ...domain.value_objects import MemberIdentity
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

    async def create(self, member: MemberCreate) -> Member:
        try:
            model = MemberModel(**member.model_dump())
            self.session.add(model)
            await self.session.flush()
            await self.session.refresh(model, ["role"])
            return Member.model_validate(model)
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
            stmt = (
                select(MemberModel)
                .options(joinedload(MemberModel.role))
                .where(MemberModel.id == id)
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            return Member.model_validate(model) if model else None
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
            await self.session.refresh(model, ["role"])
            return Member.model_validate(model)
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
                .options(joinedload(MemberModel.role))
                .where(
                    (MemberModel.user_id == identity.user_id) &
                    (MemberModel.room_id == identity.room_id)
                )
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            return Member.model_validate(model) if model else None
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
            role = Role.model_validate(first_row.RoleModel)
            permissions: set[Permission] = {
                Permission.model_validate(row.PermissionModel) for row in rows
            }
            return RoomRole(room_id=room_id, role=role, permissions=list(permissions))
        except SQLAlchemyError as e:
            raise ReadingError(
                f"Error while reading room role by member id {id}, error: {e}"
            ) from e
