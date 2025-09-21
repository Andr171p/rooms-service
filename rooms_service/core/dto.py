from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .constants import MemberPermissionStatus
from .value_objects import Name, PermissionCode


class _DTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class RolePermission(_DTO):
    role_id: UUID
    role_name: Name
    permission_code: PermissionCode


class MemberPermission(_DTO):
    member_id: UUID
    permission_code: PermissionCode
    status: MemberPermissionStatus
