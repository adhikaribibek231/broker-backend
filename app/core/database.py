from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    pass

url = make_url(settings.database_url)
engine_kwargs = {"pool_pre_ping": True}
if url.drivername.startswith("sqlite"):
    engine_kwargs["connect_args"] = {
        "check_same_thread": False,
    }

try:
    engine = create_engine(settings.database_url, **engine_kwargs)
except Exception as exc:
    raise RuntimeError(
        "Failed to initialize database engine from DATABASE_URL"
    ) from exc


SessionLocal = sessionmaker(bind=engine,autoflush=False,autocommit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()