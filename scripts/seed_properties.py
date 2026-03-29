from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.database import SessionLocal, engine
from app.domains.properties.model import Property
from app.domains.properties.seed import seed_sample_properties


def main() -> None:
    Property.__table__.create(bind=engine, checkfirst=True)

    db = SessionLocal()
    try:
        inserted_rows = seed_sample_properties(db)
        if not inserted_rows:
            print("Properties already initialized")
            return

        print(f"Inserted {inserted_rows} properties")
    finally:
        db.close()


if __name__ == "__main__":
    main()
