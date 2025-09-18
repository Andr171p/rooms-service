from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastauth import AuthMiddleware

from ..settings import settings


async def lifespan(_: FastAPI) -> AsyncIterator[None]: ...


def setup_middlewares(app: FastAPI) -> None:
    app.add_middleware(
        AuthMiddleware, base_url=settings.sso.base_url, realm=settings.sso.realm
    )
