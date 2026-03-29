from pathlib import Path

from sqlalchemy import inspect, text

from app.core.database import Base, SessionLocal, engine


def load_models() -> None:
    from app.domains.auth import model
    from app.domains.favorites import model
    from app.domains.properties import model
    from app.domains.users import model


def check_database_connection() -> None:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))


def ensure_user_token_version_column() -> None:
    with engine.begin() as conn:
        columns = {column["name"] for column in inspect(conn).get_columns("users")}
        if "token_version" not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN token_version INTEGER NOT NULL DEFAULT 0"))


def ensure_favorites_property_foreign_key() -> None:
    if engine.dialect.name != "sqlite":
        return

    with engine.begin() as conn:
        inspector = inspect(conn)
        if "favorites" not in inspector.get_table_names():
            return

        foreign_tables = {
            foreign_key["referred_table"]
            for foreign_key in inspector.get_foreign_keys("favorites")
            if foreign_key.get("referred_table")
        }
        if "properties" in foreign_tables:
            return

        conn.execute(text("PRAGMA foreign_keys=OFF"))
        try:
            conn.execute(
                text(
                    """
                    CREATE TABLE favorites_new (
                        id INTEGER NOT NULL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        property_id INTEGER NOT NULL,
                        created_at DATETIME NOT NULL,
                        CONSTRAINT uq_favorites_user_property UNIQUE (user_id, property_id),
                        FOREIGN KEY(user_id) REFERENCES users (id),
                        FOREIGN KEY(property_id) REFERENCES properties (id)
                    )
                    """
                )
            )
            conn.execute(
                text(
                    """
                    INSERT INTO favorites_new (id, user_id, property_id, created_at)
                    SELECT favorites.id, favorites.user_id, favorites.property_id, favorites.created_at
                    FROM favorites
                    JOIN users ON users.id = favorites.user_id
                    JOIN properties ON properties.id = favorites.property_id
                    """
                )
            )
            conn.execute(text("DROP TABLE favorites"))
            conn.execute(text("ALTER TABLE favorites_new RENAME TO favorites"))
            conn.execute(text("CREATE INDEX ix_favorites_user_id ON favorites (user_id)"))
            conn.execute(text("CREATE INDEX ix_favorites_property_id ON favorites (property_id)"))
        finally:
            conn.execute(text("PRAGMA foreign_keys=ON"))


def ensure_property_thumbnail_urls() -> int:
    load_models()

    with engine.connect() as conn:
        if "properties" not in inspect(conn).get_table_names():
            return 0

    from app.domains.properties.images import backfill_property_thumbnail_urls

    with SessionLocal() as db:
        return backfill_property_thumbnail_urls(db, assets_root=Path("app/assets"))


def ensure_schema() -> None:
    load_models()
    Base.metadata.create_all(bind=engine)
    ensure_user_token_version_column()
    ensure_favorites_property_foreign_key()
