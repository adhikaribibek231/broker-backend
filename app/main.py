import logging
from time import perf_counter
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from app.core.config import settings, configure_logging
from app.core.database import engine, Base
from app.api.routes import router


def ensure_user_token_version_column() -> None:
    with engine.begin() as conn:
        columns = {column["name"] for column in inspect(conn).get_columns("users")}
        if "token_version" not in columns:
            conn.execute(
                text("ALTER TABLE users ADD COLUMN token_version INTEGER NOT NULL DEFAULT 0")
            )


def create_app():
    configure_logging()
    logger = logging.getLogger(__name__)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("Application startup")

        try:
            logger.info("Importing orm models")
            from app.domains.users import model as _users_model
            from app.domains.auth import model as _auth_model
            from app.domains.favorites import model as _favorites_model

            logger.info("Checking database connectivity")
            started_at = perf_counter()

            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            logger.info("Database OK in %.2fs", perf_counter() - started_at)
            
            if settings.auto_create_schema:
                logger.info("Ensuring database schema")
                started_at= perf_counter()

                Base.metadata.create_all(bind=engine)
                ensure_user_token_version_column()

                logger.info("Database schema ensured in %.2fs",perf_counter()-started_at)
            else:
                logger.info("AUTO_CREATE_SCHEMA disabled, skipping schema sync")
            yield

        except Exception:
            logger.exception("Application Startup failed")
            raise

        finally:
            engine.dispose()
            logger.info("Application Shutdown")

    app = FastAPI(
        title=settings.app_display_name,
        lifespan=lifespan,
    )

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

    app.include_router(router)

    return app


app = create_app()
