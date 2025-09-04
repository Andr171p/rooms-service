from pydantic import BaseModel

from ..core.enums import RoomType, RoomVisibility


class RoomCreateSchema(BaseModel):
    type: RoomType
    name: str | None
    slug: str | None
    visibility: RoomVisibility = RoomVisibility.PUBLIC
