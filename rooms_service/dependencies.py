from typing import Final

from collections.abc import AsyncIterator

from dishka import AsyncContainer, Provider, Scope, from_context, make_async_container, provide
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .database.base import create_sessionmaker
from .settings import Settings, settings


class AppProvider(Provider):
    app_settings = from_context(provides=Settings, scope=Scope.APP)

    @provide(scope=Scope.APP)
    def get_sessionmaker(self, app_settings: Settings) -> async_sessionmaker[AsyncSession]:  # noqa: PLR6301
        return create_sessionmaker(app_settings.postgres.sqlalchemy_url)

    @provide(scope=Scope.REQUEST)
    async def get_session(  # noqa: PLR6301
            self, sessionmaker: async_sessionmaker[AsyncSession]
    ) -> AsyncIterator[AsyncSession]:
        async with sessionmaker() as session:
            yield session


container: Final[AsyncContainer] = make_async_container(
    AppProvider(), context={Settings: settings}
)
