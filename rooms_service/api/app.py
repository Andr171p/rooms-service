from fastapi import FastAPI
from fastauth import AuthMiddleware

from ..settings import settings


def setup_middlewares(app: FastAPI) -> None:
    app.add_middleware(
        AuthMiddleware, base_url=settings.sso.base_url, realm=settings.sso.realm
    )
