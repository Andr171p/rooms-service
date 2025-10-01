from typing import Final

from .constants import ADMIN_PRIORITY, GUEST_PRIORITY, MEMBER_PRIORITY, OWNER_PRIORITY
from .value_objects import (
    Name,
    Permission,
    PermissionCode,
    Role,
    RolePriority,
    RoleType,
    SystemRole,
)

# Права для гостя
GUEST_PERMISSIONS: Final[set[Permission]] = {
    Permission(code=PermissionCode("message:read"), category="message"),
    Permission(code=PermissionCode("message:react"), category="message"),
}
# Права участника
MEMBER_PERMISSIONS: Final[set[Permission]] = GUEST_PERMISSIONS | {
    Permission(code=PermissionCode("message:send"), category="message"),
    Permission(code=PermissionCode("message:pin"), category="message"),
    Permission(code=PermissionCode("media:send"), category="media"),
    Permission(code=PermissionCode("member:add"), category="member"),
}
# Права админа
ADMIN_PERMISSIONS: Final[set[Permission]] = MEMBER_PERMISSIONS | {
    Permission(code=PermissionCode("member:ban"), category="member"),
    Permission(code=PermissionCode("member:kick"), category="member"),
    Permission(code=PermissionCode("member:mute"), category="member"),
    Permission(code=PermissionCode("member:invite"), category="member"),
}
# Права для владельца ('owner')
OWNER_PERMISSIONS: Final[set[Permission]] = ADMIN_PERMISSIONS | {
    Permission(code=PermissionCode("room:manage"), category="room"),
    Permission(code=PermissionCode("role:manage"), category="role"),
    Permission(code=PermissionCode("role:create"), category="role"),
}

ROLES_REGISTRY: Final[dict[SystemRole, Role]] = {
    SystemRole.GUEST: Role(
        type=RoleType.SYSTEM,
        name=Name("guest"),
        priority=RolePriority(GUEST_PRIORITY),
        permissions=list(GUEST_PERMISSIONS),
    ),
    SystemRole.MEMBER: Role(
        type=RoleType.SYSTEM,
        name=Name("member"),
        priority=RolePriority(MEMBER_PRIORITY),
        permissions=list(MEMBER_PERMISSIONS),
    ),
    SystemRole.ADMIN: Role(
        type=RoleType.SYSTEM,
        name=Name("admin"),
        priority=RolePriority(ADMIN_PRIORITY),
        permissions=list(ADMIN_PERMISSIONS),
    ),
    SystemRole.OWNER: Role(
        type=RoleType.SYSTEM,
        name=Name("owner"),
        priority=RolePriority(OWNER_PRIORITY),
        permissions=list(OWNER_PERMISSIONS),
    )
}
