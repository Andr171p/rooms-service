from rooms_service.application.dto import SystemRoleRead
from rooms_service.domain.value_objects import RoleType

dto = SystemRoleRead(name="admin")

print(dto)
