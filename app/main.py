import logging
from contextlib import asynccontextmanager
from pathlib import Path
from time import perf_counter

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.core.config import configure_logging, settings
from app.core.database import engine
from app.core.startup import check_database_connection, ensure_property_thumbnail_urls, ensure_schema


def _log_timed_step(logger: logging.Logger, message: str, fn) -> None:
    started_at = perf_counter()
    fn()
    logger.info("%s in %.2fs", message, perf_counter() - started_at)


def create_app() -> FastAPI:
    configure_logging()
    logger = logging.getLogger(__name__)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        logger.info("Application startup")
        try:
            _log_timed_step(logger, "Database OK", check_database_connection)
            if settings.auto_create_schema:
                _log_timed_step(logger, "Database schema ensured", ensure_schema)
            else:
                logger.info("AUTO_CREATE_SCHEMA disabled, skipping schema sync")
            updated_property_images = ensure_property_thumbnail_urls()
            if updated_property_images:
                logger.info("Property thumbnail URLs updated for %s records", updated_property_images)
            else:
                logger.info("Property thumbnail URLs already up to date")
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
