from pydantic import BaseModel

from ..core.enums import RoomType


class RoomCreate(BaseModel):
    type: RoomType
    name: str
