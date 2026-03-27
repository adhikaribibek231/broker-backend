from fastapi import APIRouter

from app.api.public import auth, favorites

public_router = APIRouter(prefix="/public")
public_router.include_router(auth.router)
public_router.include_router(favorites.router)

__all__ = [public_router]
