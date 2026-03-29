import tempfile
import unittest
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.domains.properties.model import Property
from app.domains.properties.seed import SAMPLE_PROPERTIES, seed_sample_properties

from app.domains.properties import model as _properties_model


class PropertySeedTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        db_path = Path(self.tmpdir.name) / "test.db"
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
        )
        self.session_factory = sessionmaker(bind=self.engine, autoflush=False)
        Base.metadata.create_all(bind=self.engine)
        self.db = self.session_factory()

    def tearDown(self) -> None:
        self.db.close()
        self.engine.dispose()
        self.tmpdir.cleanup()

    def test_seed_sample_properties_inserts_once(self) -> None:
        inserted_rows = seed_sample_properties(self.db)
        self.assertEqual(inserted_rows, len(SAMPLE_PROPERTIES))
        self.assertEqual(self.db.query(Property).count(), len(SAMPLE_PROPERTIES))

        inserted_rows = seed_sample_properties(self.db)
        self.assertEqual(inserted_rows, 0)
        self.assertEqual(self.db.query(Property).count(), len(SAMPLE_PROPERTIES))


if __name__ == "__main__":
    unittest.main()
