import tempfile
import unittest
from pathlib import Path

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import create_engine, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.api.public.auth import login, logout, refresh, register
from app.api.public.favorites import create_favorite, delete_favorite, list_my_favorites
from app.core.database import Base
from app.domains.auth.schema import RefreshTokenIn
from app.domains.favorites.model import Favorite
from app.domains.favorites.schema import FavoriteCreate
from app.domains.properties.model import Property
from app.domains.users.schema import UserCreate, UserLogin
from app.utils.deps import get_current_user

from app.domains.auth import model as _auth_model
from app.domains.favorites import model as _favorites_model
from app.domains.properties import model as _properties_model
from app.domains.users import model as _users_model


class AuthFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        db_path = Path(self.tmpdir.name) / "test.db"
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
        )
        event.listen(self.engine, "connect", self._enable_sqlite_foreign_keys)
        self.session_factory = sessionmaker(bind=self.engine, autoflush=False)
        Base.metadata.create_all(bind=self.engine)
        self.db: Session = self.session_factory()
        self._create_property(101)

    def tearDown(self) -> None:
        self.db.close()
        self.engine.dispose()
        self.tmpdir.cleanup()

    def _register_and_login(self) -> tuple[str, str]:
        register(
            UserCreate(
                name="Auth Flow",
                username="auth-flow",
                email="auth-flow@example.com",
                password="strongpass123",
            ),
            self.db,
        )
        token_pair = login(
            UserLogin(
                email="auth-flow@example.com",
                password="strongpass123",
            ),
            self.db,
        )
        return token_pair.access_token, token_pair.refresh_token

    @staticmethod
    def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    def _create_property(self, property_id: int) -> Property:
        property_obj = Property(
            id=property_id,
            title=f"Property {property_id}",
            location="Kathmandu",
            price=100000,
            property_type="Apartment",
            image_url=f"/assets/properties/property-{property_id}.jpg",
            description="Test property",
            is_active=True,
        )
        self.db.add(property_obj)
        self.db.commit()
        return property_obj

    def _get_current_user(self, access_token: str):
        return get_current_user(
            HTTPAuthorizationCredentials(scheme="Bearer", credentials=access_token),
            self.db,
        )

    def test_logout_invalidates_current_access_token(self) -> None:
        access_token, refresh_token = self._register_and_login()

        user = self._get_current_user(access_token)
        self.assertEqual(user.email, "auth-flow@example.com")

        response = logout(RefreshTokenIn(refresh_token=refresh_token), self.db)
        self.assertEqual(response.detail, "Logged out successfully")

        with self.assertRaises(HTTPException) as exc:
            self._get_current_user(access_token)
        self.assertEqual(exc.exception.status_code, 401)

    def test_rotated_refresh_token_cannot_logout_session(self) -> None:
        _, refresh_token = self._register_and_login()
        rotated = refresh(RefreshTokenIn(refresh_token=refresh_token), self.db)

        with self.assertRaises(HTTPException) as exc:
            logout(RefreshTokenIn(refresh_token=refresh_token), self.db)
        self.assertEqual(exc.exception.status_code, 401)

        response = logout(RefreshTokenIn(refresh_token=rotated.refresh_token), self.db)
        self.assertEqual(response.detail, "Logged out successfully")

    def test_delete_favorite_returns_success_message(self) -> None:
        access_token, _ = self._register_and_login()
        current_user = self._get_current_user(access_token)

        favorite = create_favorite(FavoriteCreate(property_id=101), current_user, self.db)
        self.assertEqual(favorite.property_id, 101)
        self.assertEqual(len(list_my_favorites(current_user, self.db)), 1)

        response = delete_favorite(101, current_user, self.db)
        self.assertEqual(response.detail, "Favorite removed successfully")
        self.assertEqual(list_my_favorites(current_user, self.db), [])

    def test_cannot_favorite_unknown_property(self) -> None:
        access_token, _ = self._register_and_login()
        current_user = self._get_current_user(access_token)

        with self.assertRaises(HTTPException) as exc:
            create_favorite(FavoriteCreate(property_id=9999), current_user, self.db)
        self.assertEqual(exc.exception.status_code, 400)
        self.assertEqual(exc.exception.detail, "Property not found")

    def test_database_rejects_favorite_for_missing_property(self) -> None:
        access_token, _ = self._register_and_login()
        current_user = self._get_current_user(access_token)

        self.db.add(Favorite(user_id=current_user.id, property_id=9999))
        with self.assertRaises(IntegrityError):
            self.db.commit()
        self.db.rollback()


if __name__ == "__main__":
    unittest.main()
