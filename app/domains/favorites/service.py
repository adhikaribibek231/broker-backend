from sqlalchemy.orm import Session

from app.domains.favorites.model import Favorite
from app.domains.properties.service import get_property_by_id


def get_favorite(db: Session, user_id: int, property_id: int) -> Favorite | None:
    return (
        db.query(Favorite)
        .filter(Favorite.user_id == user_id, Favorite.property_id == property_id)
        .one_or_none()
    )


def list_favorites_for_user(db: Session, user_id: int) -> list[Favorite]:
    return (
        db.query(Favorite)
        .filter(Favorite.user_id == user_id)
        .order_by(Favorite.created_at.desc())
        .all()
    )


def add_favorite(db: Session, user_id: int, property_id: int) -> Favorite:
    property_obj = get_property_by_id(db, property_id)
    if property_obj is None:
        raise ValueError("Property not found")

    if get_favorite(db, user_id, property_id):
        raise ValueError("Property already in favorites")

    favorite = Favorite(user_id=user_id, property_id=property_id)
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite


def remove_favorite(db: Session, user_id: int, property_id: int) -> bool:
    favorite = get_favorite(db, user_id, property_id)
    if not favorite:
        return False

    db.delete(favorite)
    db.commit()
    return True
