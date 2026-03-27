from fastapi import APIRouter

from app.api.public import public_router

router = APIRouter(prefix="/api/v1")
router.include_router(public_router)