from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import (
    Base,
    DatetimeDefault,
    JsonDict,
    PostgresUUID,
    StrNullable,
    StrUnique,
    TextNullable,
)


class RoomModel(Base):
    __tablename__ = "rooms"

    type: Mapped[str]
    avatar_url: Mapped[StrNullable]
    name: Mapped[StrNullable]
    created_by: Mapped[PostgresUUID]

    members: Mapped[list["MemberModel"]] = relationship(
        back_populates="room", cascade="all, delete-orphan"
    )
    roles_permissions: Mapped[list["RolePermissionModel"]] = relationship(back_populates="room")
    properties: Mapped["RoomPropertiesModel"] = relationship(
        back_populates="room", cascade="all, delete-orphan", uselist=False
    )


class RoomPropertiesModel(Base):
    __tablename__ = "rooms_properties"

    room_id: Mapped[UUID] = mapped_column(ForeignKey("rooms.id"), unique=True)
    visibility: Mapped[str]
    max_members: Mapped[int]
    messages: Mapped[JsonDict]
    media: Mapped[JsonDict]
    privacy: Mapped[JsonDict]

    room: Mapped["RoomModel"] = relationship(back_populates="settings")


class MemberModel(Base):
    __tablename__ = "members"

    user_id: Mapped[PostgresUUID]
    room_id: Mapped[UUID] = mapped_column(ForeignKey("rooms.id"), unique=False)
    role_id: Mapped[UUID] = mapped_column(ForeignKey("roles.id"), unique=False)
    status: Mapped[str]
    joined_at: Mapped[DatetimeDefault]

    room: Mapped["RoomModel"] = relationship(back_populates="members")
    role: Mapped["RoleModel"] = relationship(back_populates="members")

    __table_args__ = (UniqueConstraint(
        "user_id", "room_id", name="unique_member"),
    )


class RoleModel(Base):
    __tablename__ = "roles"

    type: Mapped[str]
    name: Mapped[StrUnique]
    description: Mapped[TextNullable]
    priority: Mapped[int]

    roles_permissions: Mapped[list["RolePermissionModel"]] = relationship(
        back_populates="role", cascade="all, delete-orphan"
    )


class PermissionModel(Base):
    __tablename__ = "permissions"

    code: Mapped[str]
    category: Mapped[str]

    roles_permissions: Mapped[list["RolePermissionModel"]] = relationship(
        back_populates="permission", cascade="all, delete-orphan"
    )


class RolePermissionModel(Base):
    __tablename__ = "roles_permissions"

    room_id: Mapped[UUID] = mapped_column(ForeignKey("rooms.id"), unique=False)
    role_id: Mapped[UUID] = mapped_column(ForeignKey("roles.id"), unique=False)
    permission_id: Mapped[UUID] = mapped_column(ForeignKey("permissions.id"), unique=False)
    granted_by: Mapped[PostgresUUID]

    role: Mapped["RoleModel"] = relationship(back_populates="roles_permissions")
    permission: Mapped["PermissionModel"] = relationship(back_populates="roles_permissions")
    room: Mapped["RoomModel"] = relationship(back_populates="roles_permissions")

    __table_args__ = (
        UniqueConstraint("room_id", "role_id", "permission_id", name="unique_role_permission"),
    )
