from typing import Final

from collections.abc import AsyncIterator

from dishka import AsyncContainer, Provider, Scope, from_context, make_async_container, provide
from sqlalchemy.ext.asyncio import AsyncSession

from .database.base import sessionmaker
from .settings import Settings, settings


class AppProvider(Provider):
    app_settings = from_context(provides=Settings, scope=Scope.APP)

    @provide(scope=Scope.REQUEST)
    async def get_session() -> AsyncIterator[AsyncSession]:
        async with sessionmaker() as session:
            yield session


container: Final[AsyncContainer] = make_async_container(
    AppProvider(), context={Settings: settings}
)
