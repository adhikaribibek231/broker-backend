from sqlalchemy.orm import Session

from app.domains.properties.model import Property

def list_properties(db: Session) -> list[Property]:
    return (
        db.query(Property)
        .filter(Property.is_active == True)
        .order_by(Property.id.asc())
        .all()
    )


def get_property_by_id(db: Session, property_id: int) -> Property | None:
    return (
        db.query(Property)
        .filter(
            Property.id == property_id,
            Property.is_active == True,
        )
        .first()
    )
