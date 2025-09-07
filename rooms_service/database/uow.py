from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.base import UnitOfWork
from .repository import SQLMemberRepository, SQLRoomRepository


class SQLUnitOfWork(UnitOfWork):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def __aenter__(self) -> Self:
        await self.session.begin()
        self.room_repository = SQLRoomRepository(self.session)
        self.member_repository = SQLMemberRepository(self.session)
        return self

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
