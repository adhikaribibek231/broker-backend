from sqlalchemy.orm import Session

from app.domains.properties.images import build_thumbnail_image_url
from app.domains.properties.model import Property

SAMPLE_PROPERTIES = [
    {
        "title": "Modern Apartment in Kathmandu",
        "location": "Kathmandu",
        "price": 120000,
        "property_type": "Apartment",
        "image_url": build_thumbnail_image_url("/assets/properties/modern-apartment-kathmandu.jpg"),
        "description": "A modern 2-bedroom apartment in the city center.",
        "is_active": True,
    },
    {
        "title": "Family House in Lalitpur",
        "location": "Lalitpur",
        "price": 250000,
        "property_type": "House",
        "image_url": build_thumbnail_image_url("/assets/properties/family-house-lalitpur.jpg"),
        "description": "A spacious family house with parking and garden.",
        "is_active": True,
    },
    {
        "title": "Studio Flat in Bhaktapur",
        "location": "Bhaktapur",
        "price": 80000,
        "property_type": "Studio",
        "image_url": build_thumbnail_image_url("/assets/properties/studio-flat-bhaktapur.jpg"),
        "description": "Compact studio flat suitable for a single buyer.",
        "is_active": True,
    },
    {
        "title": "Luxury Villa in Pokhara",
        "location": "Pokhara",
        "price": 500000,
        "property_type": "Villa",
        "image_url": build_thumbnail_image_url("/assets/properties/luxury-villa-pokhara.jpg"),
        "description": "Premium villa with mountain views and large outdoor space.",
        "is_active": True,
    },
    {
        "title": "Commercial Space in Butwal",
        "location": "Butwal",
        "price": 300000,
        "property_type": "Commercial",
        "image_url": build_thumbnail_image_url("/assets/properties/commercial-space-butwal.jpg"),
        "description": "Well-located commercial property for office or retail use.",
        "is_active": True,
    },
]


def seed_sample_properties(db: Session) -> int:
    if db.query(Property).count() > 0:
        return 0

    for item in SAMPLE_PROPERTIES:
        db.add(Property(**item))
    db.commit()
    return len(SAMPLE_PROPERTIES)
