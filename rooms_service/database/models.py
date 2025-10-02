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
)


class RoomModel(Base):
    __tablename__ = "rooms"

    created_by: Mapped[PostgresUUID]
    type: Mapped[str]
    avatar_url: Mapped[StrNullable]
    name: Mapped[StrNullable]
    slug: Mapped[StrNullable]
    visibility: Mapped[str]
    member_count: Mapped[int]
    version: Mapped[int]

    settings: Mapped["RoomSettingsModel"] = relationship(
        back_populates="room", cascade="all, delete-orphan", uselist=False
    )
    members: Mapped[list["MemberModel"]] = relationship(
        back_populates="room", cascade="all, delete-orphan"
    )
    room_roles: Mapped[list["RoomRoleModel"]] = relationship(back_populates="room")


class RoomSettingsModel(Base):
    __tablename__ = "room_settings"

    room_id: Mapped[UUID] = mapped_column(ForeignKey("rooms.id"), unique=True)
    members: Mapped[JsonDict]
    messages: Mapped[JsonDict]
    media: Mapped[JsonDict]

    room: Mapped["RoomModel"] = relationship(back_populates="settings")


class MemberModel(Base):
    __tablename__ = "members"

    user_id: Mapped[PostgresUUID]
    room_id: Mapped[UUID] = mapped_column(ForeignKey("rooms.id"), unique=False)
    room_role_id: Mapped[UUID] = mapped_column(ForeignKey("room_roles.id"), unique=False)
    status: Mapped[str]
    joined_at: Mapped[DatetimeDefault]

    room: Mapped["RoomModel"] = relationship(back_populates="members")
    room_role: Mapped["RoomRoleModel"] = relationship(back_populates="member")
    member_permissions: Mapped[list["MemberPermissionModel"]] = relationship(
        back_populates="member"
    )

    __table_args__ = (UniqueConstraint(
        "user_id", "room_id", name="unique_member"),
    )


class RoomRoleModel(Base):
    """Роли внутри комнаты"""
    __tablename__ = "room_roles"

    room_id: Mapped[UUID] = mapped_column(ForeignKey("rooms.id"), unique=False)
    role_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("roles.id"), unique=False, nullable=True
    )
    name: Mapped[str]
    description: Mapped[StrNullable]
    priority: Mapped[int]
    is_default: Mapped[bool]

    room: Mapped["RoomModel"] = relationship(back_populates="room_roles")
    role: Mapped["RoleModel"] = relationship(back_populates="room_roles")
    member: Mapped["MemberModel"] = relationship(back_populates="room_roles")
    room_role_permissions: Mapped[list["RoomRolePermissionModel"]] = relationship(
        back_populates="room_role", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("room_id", "name", name="unique_room_role"),
    )


class RoomRolePermissionModel(Base):
    """Права для кастомных ролей внутри комнаты"""
    __tablename__ = "room_role_permissions"

    room_role_id: Mapped[UUID] = mapped_column(ForeignKey("room_roles.id"), unique=False)
    permission_id: Mapped[UUID] = mapped_column(ForeignKey("permissions.id"), unique=False)

    room_role: Mapped["RoomRoleModel"] = relationship(back_populates="room_role_permissions")
    permission: Mapped["PermissionModel"] = relationship(back_populates="room_role_permissions")

    __table_args__ = (
        UniqueConstraint("room_role_id", "permission_id", name="unique_room_role_permission"),
    )


class RoleModel(Base):
    __tablename__ = "system_roles"

    type: Mapped[str]
    name: Mapped[StrUnique]
    priority: Mapped[int]

    role_permissions: Mapped[list["RolePermissionModel"]] = relationship(
        back_populates="role", cascade="all, delete-orphan"
    )
    room_roles: Mapped[list["RoomRoleModel"]] = relationship(
        back_populates="role", cascade="all, delete-orphan"
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
    room_role_permissions: Mapped[list["RoomRolePermissionModel"]] = relationship(
        back_populates="permission", cascade="all, delete-orphan"
    )


class RolePermissionModel(Base):
    __tablename__ = "role_permissions"

    role_id: Mapped[UUID] = mapped_column(ForeignKey("roles.id"), unique=False)
    permission_id: Mapped[UUID] = mapped_column(ForeignKey("permissions.id"), unique=False)

    role: Mapped["RoleModel"] = relationship(back_populates="role_permissions")
    permission: Mapped["PermissionModel"] = relationship(back_populates="role_permissions")

    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="unique_role_permission"),
    )


class MemberPermissionModel(Base):
    __tablename__ = "member_permissions"

    member_id: Mapped[UUID] = mapped_column(ForeignKey("members.id"), unique=False)
    permission_id: Mapped[UUID] = mapped_column(ForeignKey("permissions.id"), unique=False)
    status: Mapped[str] = mapped_column(default="grant")
    granted_by: Mapped[PostgresUUID]

    member: Mapped["MemberModel"] = relationship(back_populates="member_permissions")
    permission: Mapped["PermissionModel"] = relationship(back_populates="member_permissions")

    __table_args__ = (
        UniqueConstraint("member_id", "permission_id", name="unique_member_permission"),
    )
