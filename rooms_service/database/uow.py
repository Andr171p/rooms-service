from __future__ import annotations

from typing import Any, Self

from collections.abc import Iterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.base import CRUDRepository, UnitOfWork
from .repository import SQLMemberRepository, SQLRoomRepository


class SQLRepositoryDescriptor:
    def __init__(self, repository_class: type[CRUDRepository]) -> None:
        self.repository_class = repository_class
        self.attr_name = f"_{repository_class.__name__}_"

    def __get__(self, instance: SQLUnitOfWork, owner: type) -> Any:
        if instance is None:
            return self
        if not hasattr(instance, self.attr_name):
            repository = self.repository_class(instance.session)
            setattr(instance, self.attr_name, repository)
        return getattr(instance, self.attr_name)


class SQLUnitOfWork(UnitOfWork):
    room_repository = SQLRepositoryDescriptor(SQLRoomRepository)
    member_repository = SQLRepositoryDescriptor(SQLMemberRepository)

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def __aenter__(self) -> Self:
        return self

    @asynccontextmanager
    async def transaction(self) -> Iterator[Self]:
        async with self.session.begin():
            yield self

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
