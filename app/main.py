import logging
from contextlib import asynccontextmanager
from pathlib import Path
from time import perf_counter

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text

from app.api.routes import router
from app.core.config import configure_logging, settings
from app.core.database import Base, engine, SessionLocal


def load_models() -> None:
    from app.domains.auth import model
    from app.domains.favorites import model
    from app.domains.users import model
    from app.domains.properties import model


def ensure_user_token_version_column() -> None:
    with engine.begin() as conn:
        columns = {column["name"] for column in inspect(conn).get_columns("users")}
        if "token_version" not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN token_version INTEGER NOT NULL DEFAULT 0"))

def seed_initial_data() -> None:
    from app.domains.properties.service import seed_properties

    db = SessionLocal()
    try:
        seed_properties(db)
    finally:
        db.close()

def _log_timed_step(logger: logging.Logger, message: str, fn) -> None:
    started_at = perf_counter()
    fn()
    logger.info("%s in %.2fs", message, perf_counter() - started_at)


def _check_database_connection() -> None:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))


def _ensure_schema() -> None:
    load_models()
    Base.metadata.create_all(bind=engine)
    ensure_user_token_version_column()


def create_app() -> FastAPI:
    configure_logging()
    logger = logging.getLogger(__name__)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        logger.info("Application startup")
        try:
            _log_timed_step(logger, "Database OK", _check_database_connection)
            if settings.auto_create_schema:
                _log_timed_step(logger, "Database schema ensured", _ensure_schema)
            else:
                logger.info("AUTO_CREATE_SCHEMA disabled, skipping schema sync")
            _log_timed_step(logger, "Seeded initial data", seed_initial_data)
            yield
        except Exception:
            logger.exception("Application startup failed")
            raise
        finally:
            engine.dispose()
            logger.info("Application shutdown")

    app = FastAPI(title=settings.app_display_name, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    assets_dir = Path("app/assets")
    assets_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")


    app.include_router(router)
    return app


app = create_app()
