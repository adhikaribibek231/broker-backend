from fastapi import APIRouter

from app.api.public import auth, favorites, properties

public_router = APIRouter(prefix="/public")
public_router.include_router(auth.router)
public_router.include_router(favorites.router)
public_router.include_router(properties.router)

__all__ = ["public_router"]
