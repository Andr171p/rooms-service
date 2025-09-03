from typing import Final

from dishka import AsyncContainer, Provider, Scope, from_context, make_async_container

from .settings import Settings, settings


class AppProvider(Provider):
    app_settings = from_context(provides=Settings, scope=Scope.APP)


container: Final[AsyncContainer] = make_async_container(
    AppProvider(), context={Settings: settings}
)
