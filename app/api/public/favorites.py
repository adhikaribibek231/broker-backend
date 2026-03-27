import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.favorites.schema import FavoriteCreate, FavoriteResponse
from app.domains.favorites.service import (
    add_favorite,
    list_favorites_for_user,
    remove_favorite,
)
from app.domains.users.model import User
from app.utils.deps import get_current_user

router = APIRouter(prefix="/favorites", tags=["Favorites"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=list[FavoriteResponse])
def list_my_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list_favorites_for_user(db, current_user.id)


@router.post("/", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
def create_favorite(
    payload: FavoriteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        favorite = add_favorite(db, current_user.id, payload.property_id)
        logger.info(
            "Favorite added: user_id=%s property_id=%s",
            current_user.id,
            payload.property_id,
        )
        return favorite
    except ValueError as exc:
        logger.warning(
            "Add favorite failed: user_id=%s property_id=%s reason=%s",
            current_user.id,
            payload.property_id,
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_favorite(
    property_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    removed = remove_favorite(db, current_user.id, property_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found",
        )

    logger.info(
        "Favorite removed: user_id=%s property_id=%s",
        current_user.id,
        property_id,
    )