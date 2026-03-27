import logging
from time import perf_counter
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.core.config import settings
from app.core.database import engine, Base
from app.api.routes import router


def create_app():
    logger = logging.getLogger(__name__)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("Application startup")

        try:
            from app.domains.users import model as _users_model
            from app.domains.favorites import model as _fav_model

            logger.info("Checking database connectivity")
            start = perf_counter()

            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            logger.info("Database OK in %.2fs", perf_counter() - start)

            logger.info("Creating database schema")
            Base.metadata.create_all(bind=engine)

            yield

        except Exception:
            logger.exception("Startup failed")
            raise

        finally:
            logger.info("Shutting down application")
            engine.dispose()

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