from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.database import SessionLocal, engine
from app.domains.properties.model import Property


SAMPLE_PROPERTIES = [
    {
        "title": "Modern Apartment in Kathmandu",
        "location": "Kathmandu",
        "price": 120000,
        "property_type": "Apartment",
        "image_url": "/assets/properties/modern-apartment-kathmandu.jpg",
        "description": "A modern 2-bedroom apartment in the city center.",
        "is_active": True,
    },
    {
        "title": "Family House in Lalitpur",
        "location": "Lalitpur",
        "price": 250000,
        "property_type": "House",
        "image_url": "/assets/properties/family-house-lalitpur.jpg",
        "description": "A spacious family house with parking and garden.",
        "is_active": True,
    },
    {
        "title": "Studio Flat in Bhaktapur",
        "location": "Bhaktapur",
        "price": 80000,
        "property_type": "Studio",
        "image_url": "/assets/properties/studio-flat-bhaktapur.jpg",
        "description": "Compact studio flat suitable for a single buyer.",
        "is_active": True,
    },
    {
        "title": "Luxury Villa in Pokhara",
        "location": "Pokhara",
        "price": 500000,
        "property_type": "Villa",
        "image_url": "/assets/properties/luxury-villa-pokhara.jpg",
        "description": "Premium villa with mountain views and large outdoor space.",
        "is_active": True,
    },
    {
        "title": "Commercial Space in Butwal",
        "location": "Butwal",
        "price": 300000,
        "property_type": "Commercial",
        "image_url": "/assets/properties/commercial-space-butwal.jpg",
        "description": "Well-located commercial property for office or retail use.",
        "is_active": True,
    },
]


def main() -> None:
    Property.__table__.create(bind=engine, checkfirst=True)

    db = SessionLocal()
    try:
        if db.query(Property).count() > 0:
            print("Properties already initialized")
            return

        for item in SAMPLE_PROPERTIES:
            db.add(Property(**item))
        db.commit()
        print(f"Inserted {len(SAMPLE_PROPERTIES)} properties")
    finally:
        db.close()


if __name__ == "__main__":
    main()
