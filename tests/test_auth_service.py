from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
import unittest

from app.domains.auth.service import is_refresh_token_valid


def make_row(*, revoked: bool, expires_at: datetime) -> SimpleNamespace:
    return SimpleNamespace(
        id=1,
        user_id=123,
        revoked=revoked,
        expires_at=expires_at,
    )


class IsRefreshTokenValidTests(unittest.TestCase):
    def test_accepts_future_aware_expiry(self) -> None:
        row = make_row(
            revoked=False,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )

        self.assertTrue(is_refresh_token_valid(row))

    def test_accepts_future_naive_expiry_from_sqlite(self) -> None:
        row = make_row(
            revoked=False,
            expires_at=(datetime.now(timezone.utc) + timedelta(minutes=5)).replace(tzinfo=None),
        )

        self.assertTrue(is_refresh_token_valid(row))

    def test_rejects_expired_naive_expiry_from_sqlite(self) -> None:
        row = make_row(
            revoked=False,
            expires_at=(datetime.now(timezone.utc) - timedelta(minutes=5)).replace(tzinfo=None),
        )

        self.assertFalse(is_refresh_token_valid(row))

    def test_rejects_revoked_token(self) -> None:
        row = make_row(
            revoked=True,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )

        self.assertFalse(is_refresh_token_valid(row))


if __name__ == "__main__":
    unittest.main()
