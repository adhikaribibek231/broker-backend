import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base
from app.domains.users.schema import UserCreate
from app.domains.users.service import create_user

from app.domains.users import model as _users_model  # noqa: F401


class UserValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        db_path = Path(self.tmpdir.name) / "test.db"
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

    def test_user_create_rejects_blank_name(self) -> None:
        with self.assertRaises(ValidationError):
            UserCreate(
                name="   ",
                username="buyer-one",
                email="buyer-one@example.com",
                password="strongpass123",
            )

    def test_user_create_rejects_blank_username(self) -> None:
        with self.assertRaises(ValidationError):
            UserCreate(
                name="Buyer One",
                username="   ",
                email="buyer-one@example.com",
                password="strongpass123",
            )

    def test_user_create_rejects_trimmed_short_username(self) -> None:
        with self.assertRaises(ValidationError):
            UserCreate(
                name="Buyer One",
                username=" ab ",
                email="buyer-one@example.com",
                password="strongpass123",
            )

    def test_create_user_rejects_blank_name_when_called_directly(self) -> None:
        with self.assertRaises(ValueError):
            create_user(
                self.db,
                SimpleNamespace(
                    name="   ",
                    username="buyer-one",
                    email="buyer-one@example.com",
                    password="strongpass123",
                ),
            )

    def test_create_user_rejects_trimmed_short_username_when_called_directly(self) -> None:
        with self.assertRaises(ValueError):
            create_user(
                self.db,
                SimpleNamespace(
                    name="Buyer One",
                    username=" ab ",
                    email="buyer-one@example.com",
                    password="strongpass123",
                ),
            )


if __name__ == "__main__":
    unittest.main()
