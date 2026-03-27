from sqlalchemy.orm import Session

from app.domains.properties.model import Property


SAMPLE_PROPERTIES = [
    {
        "title": "Modern Apartment in Kathmandu",
        "location": "Kathmandu",
        "price": 120000,
        "property_type": "Apartment",
        "image_url": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85",
        "description": "A modern 2-bedroom apartment in the city center.",
        "is_active": True,
    },
    {
        "title": "Family House in Lalitpur",
        "location": "Lalitpur",
        "price": 250000,
        "property_type": "House",
        "image_url": "https://images.unsplash.com/photo-1564013799919-ab600027ffc6",
        "description": "A spacious family house with parking and garden.",
        "is_active": True,
    },
    {
        "title": "Studio Flat in Bhaktapur",
        "location": "Bhaktapur",
        "price": 80000,
        "property_type": "Studio",
        "image_url": "https://images.unsplash.com/photo-1494526585095-c41746248156",
        "description": "Compact studio flat suitable for a single buyer.",
        "is_active": True,
    },
    {
        "title": "Luxury Villa in Pokhara",
        "location": "Pokhara",
        "price": 500000,
        "property_type": "Villa",
        "image_url": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750",
        "description": "Premium villa with mountain views and large outdoor space.",
        "is_active": True,
    },
    {
        "title": "Commercial Space in Butwal",
        "location": "Butwal",
        "price": 300000,
        "property_type": "Commercial",
        "image_url": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab",
        "description": "Well-located commercial property for office or retail use.",
        "is_active": True,
    },
]


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


def seed_properties(db: Session) -> None:
    existing_count = db.query(Property).count()
    if existing_count > 0:
        return

    for item in SAMPLE_PROPERTIES:
        db.add(Property(**item))

    db.commit()