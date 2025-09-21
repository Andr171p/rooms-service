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

    created_by: Mapped[PostgresUUID]
    type: Mapped[str]
    avatar_url: Mapped[StrNullable]
    name: Mapped[StrNullable]
    slug: Mapped[StrNullable]
    visibility: Mapped[str]

    settings: Mapped["RoomSettingsModel"] = relationship(
        back_populates="room", cascade="all, delete-orphan", uselist=False
    )
    members: Mapped[list["MemberModel"]] = relationship(
        back_populates="room", cascade="all, delete-orphan"
    )
    room_roles: Mapped[list["RoomRoleModel"]] = relationship(back_populates="room")


class RoomSettingsModel(Base):
    __tablename__ = "rooms_settings"

    room_id: Mapped[UUID] = mapped_column(ForeignKey("rooms.id"), unique=True)
    members: Mapped[JsonDict]
    messages: Mapped[JsonDict]
    media: Mapped[JsonDict]

    room: Mapped["RoomModel"] = relationship(back_populates="settings")


class MemberModel(Base):
    __tablename__ = "members"

    user_id: Mapped[PostgresUUID]
    room_id: Mapped[UUID] = mapped_column(ForeignKey("rooms.id"), unique=False)
    role_id: Mapped[UUID] = mapped_column(ForeignKey("room_roles.id"), unique=False)
    status: Mapped[str]
    joined_at: Mapped[DatetimeDefault]

    room: Mapped["RoomModel"] = relationship(back_populates="members")
    room_role: Mapped["RoomRoleModel"] = relationship(back_populates="members")
    member_permissions: Mapped[list["MemberPermissionModel"]] = relationship(
        back_populates="member", cascade="all, delete-orphan"
    )

    __table_args__ = (UniqueConstraint(
        "user_id", "room_id", name="unique_member"),
    )


class RoleModel(Base):
    __tablename__ = "roles"

    type: Mapped[str]
    name: Mapped[StrUnique]
    description: Mapped[TextNullable]
    priority: Mapped[int]

    role_permissions: Mapped[list["RolePermissionModel"]] = relationship(
        back_populates="role", cascade="all, delete-orphan"
    )
    room_roles: Mapped[list["RoomRoleModel"]] = relationship(back_populates="role")


class RoomRoleModel(Base):
    __tablename__ = "room_roles"

    room_id: Mapped[UUID] = mapped_column(ForeignKey("rooms.id"), unique=False)
    role_id: Mapped[UUID] = mapped_column(ForeignKey("roles.id"), unique=False)

    room: Mapped["RoomModel"] = relationship(back_populates="room_roles")
    role: Mapped["RoleModel"] = relationship(back_populates="room_roles")
    members: Mapped[list["MemberModel"]] = relationship(back_populates="room_role")

    __table_args__ = (
        UniqueConstraint("room_id", "role_id", name="unique_room_role"),
    )


class PermissionModel(Base):
    __tablename__ = "permissions"

    code: Mapped[StrUnique]
    category: Mapped[str]

    role_permissions: Mapped[list["RolePermissionModel"]] = relationship(
        back_populates="permission", cascade="all, delete-orphan"
    )
    member_permissions: Mapped[list["MemberPermissionModel"]] = relationship(
        back_populates="permission", cascade="all, delete-orphan"
    )


class RolePermissionModel(Base):
    __tablename__ = "role_permissions"

    role_id: Mapped[UUID] = mapped_column(ForeignKey("roles.id"), unique=False)
    permission_code: Mapped[UUID] = mapped_column(ForeignKey("permissions.code"), unique=False)

    role: Mapped["RoleModel"] = relationship(back_populates="role_permissions")
    permission: Mapped["PermissionModel"] = relationship(back_populates="role_permissions")

    __table_args__ = (
        UniqueConstraint("role_id", "permission_code", name="unique_role_permission"),
    )


class MemberPermissionModel(Base):
    __tablename__ = "member_permissions"

    member_id: Mapped[UUID] = mapped_column(ForeignKey("members.id"), unique=True)
    permission_code: Mapped[UUID] = mapped_column(ForeignKey("permissions.code"), unique=False)
    status: Mapped[str] = mapped_column(default="grant")

    member: Mapped["MemberModel"] = relationship(back_populates="member_permissions")
    permission: Mapped["PermissionModel"] = relationship(back_populates="member_permissions")

    __table_args__ = (
        UniqueConstraint("member_id", "permission_code", name="unique_member_permission"),
    )
