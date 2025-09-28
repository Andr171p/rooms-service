from abc import ABC
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .entities import Permission, Role
from .events import EventT
from .value_objects import Id, PermissionCode


class AggregateRoot(BaseModel, ABC):
    id: Id
    _events: list[EventT] = Field(default_factory=list, exclude=True)
    _version: str = Field(default="0.1.0", exclude=True)

    model_config = ConfigDict(
        arbitrary_types_allowed=True, validate_assignment=True, frozen=False
    )


class RoomRole(BaseModel):
    """Роль пользователя в конкретной комнате с набором разрешений.
    Объединяет роль и её разрешения для обеспечения целостности правил доступа.
    """
    room_id: UUID
    role: Role
    permissions: list[Permission]

    def add_permission(self, permission: Permission) -> None:
        """Добавляет разрешение в роль, если его ещё нет.

        :param permission: Сущность разрешения.
        """
        if permission not in self.permissions:
            self.permissions.append(permission)

    def has_permission(self, permission_code: PermissionCode) -> bool:
        """Проверяет наличие конкретного разрешения к роли.

        :param permission_code: Уникальный код разрешения конкретного действия.
        """
        return any(permission.code == permission_code for permission in self.permissions)
