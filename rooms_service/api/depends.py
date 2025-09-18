from typing import Annotated, Any

from collections.abc import Callable, Coroutine
from uuid import UUID

from dishka.integrations.fastapi import FromDishka
from fastapi import Depends, HTTPException, Path, status
from fastauth import CurrentUser

from ..core.value_objects import PermissionCode
from ..services import PermissionService

RoomId = Annotated[UUID, Path(..., description="ID комнаты")]


def require_permission(
        permission_code: PermissionCode
) -> Callable[[UUID, CurrentUser, PermissionService], Coroutine[Any, Any, bool]]:
    async def permission_checker(
            id: RoomId,  # noqa: A002
            current_user: CurrentUser,
            service: FromDishka[PermissionService],
    ) -> bool:
        has_permission = await service.has_permission(
            room_id=id, user_id=current_user.x_user_id, permission_code=permission_code
        )
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied for this room",
            )
        return True
    return permission_checker


RequirePermission = Annotated[bool, Depends(require_permission)]
