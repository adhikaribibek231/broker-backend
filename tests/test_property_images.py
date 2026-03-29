import tempfile
import unittest
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base
from app.domains.properties.images import (
    backfill_property_thumbnail_urls,
    build_thumbnail_image_url,
)
from app.domains.properties.model import Property

from app.domains.properties import model as _properties_model  # noqa: F401


class PropertyImageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        db_path = Path(self.tmpdir.name) / "test.db"
        self.assets_root = Path(self.tmpdir.name) / "assets"
        self.properties_dir = self.assets_root / "properties"
        self.properties_dir.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
        )
        self.session_factory = sessionmaker(bind=self.engine, autoflush=False)
        Base.metadata.create_all(bind=self.engine)
        self.db: Session = self.session_factory()

    def tearDown(self) -> None:
        self.db.close()
        self.engine.dispose()
        self.tmpdir.cleanup()

    def test_build_thumbnail_image_url_switches_to_thumb_variant(self) -> None:
        self.assertEqual(
            build_thumbnail_image_url("/assets/properties/modern-apartment-kathmandu.jpg"),
            "/assets/properties/modern-apartment-kathmandu-thumb.webp",
        )

    def test_backfill_updates_image_url_when_thumbnail_exists(self) -> None:
        property_obj = Property(
            title="Modern Apartment",
            location="Kathmandu",
            price=120000,
            property_type="Apartment",
            image_url="/assets/properties/modern-apartment-kathmandu.jpg",
            description="A modern apartment",
            is_active=True,
        )
        self.db.add(property_obj)
        self.db.commit()

        (self.properties_dir / "modern-apartment-kathmandu-thumb.webp").touch()

        updated_rows = backfill_property_thumbnail_urls(self.db, self.assets_root)
        self.db.refresh(property_obj)

        self.assertEqual(updated_rows, 1)
        self.assertEqual(
            property_obj.image_url,
            "/assets/properties/modern-apartment-kathmandu-thumb.webp",
        )

    def test_backfill_leaves_original_when_thumbnail_missing(self) -> None:
        property_obj = Property(
            title="Modern Apartment",
            location="Kathmandu",
            price=120000,
            property_type="Apartment",
            image_url="/assets/properties/modern-apartment-kathmandu.jpg",
            description="A modern apartment",
            is_active=True,
        )
        self.db.add(property_obj)
        self.db.commit()

        updated_rows = backfill_property_thumbnail_urls(self.db, self.assets_root)
        self.db.refresh(property_obj)

        self.assertEqual(updated_rows, 0)
        self.assertEqual(
            property_obj.image_url,
            "/assets/properties/modern-apartment-kathmandu.jpg",
        )


if __name__ == "__main__":
    unittest.main()
