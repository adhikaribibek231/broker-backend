import os
import unittest
from unittest.mock import patch

from app.core.config import Settings, parse_cors_allowed_origins


class ConfigTests(unittest.TestCase):
    def test_parse_cors_allowed_origins_strips_trailing_slashes(self) -> None:
        self.assertEqual(
            parse_cors_allowed_origins(
                " http://localhost:3000/ , https://broker-frontend.vercel.app/ "
            ),
            [
                "http://localhost:3000",
                "https://broker-frontend.vercel.app",
            ],
        )

    def test_settings_accepts_comma_separated_cors_origins(self) -> None:
        settings = Settings(
            JWT_SECRET_KEY="test-secret",
            CORS_ALLOWED_ORIGINS="http://localhost:3000/, https://example.com/",
        )

        self.assertEqual(
            settings.cors_allowed_origins,
            [
                "http://localhost:3000",
                "https://example.com",
            ],
        )

    def test_settings_reads_comma_separated_cors_origins_from_env(self) -> None:
        with patch.dict(
            os.environ,
            {
                "JWT_SECRET_KEY": "test-secret",
                "CORS_ALLOWED_ORIGINS": "http://localhost:3000/, https://example.com/",
            },
            clear=False,
        ):
            settings = Settings()

        self.assertEqual(
            settings.cors_allowed_origins,
            [
                "http://localhost:3000",
                "https://example.com",
            ],
        )

    def test_settings_reads_json_cors_origins_from_env(self) -> None:
        with patch.dict(
            os.environ,
            {
                "JWT_SECRET_KEY": "test-secret",
                "CORS_ALLOWED_ORIGINS": '["http://localhost:3000/", "https://example.com/"]',
            },
            clear=False,
        ):
            settings = Settings()

        self.assertEqual(
            settings.cors_allowed_origins,
            [
                "http://localhost:3000",
                "https://example.com",
            ],
        )


if __name__ == "__main__":
    unittest.main()
