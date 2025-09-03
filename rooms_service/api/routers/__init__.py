__all__ = (
    "rooms_router",
)

from fastapi import APIRouter

from .rooms import rooms_router

router = APIRouter(prefix="/api/v1")

router.include_router(rooms_router)
