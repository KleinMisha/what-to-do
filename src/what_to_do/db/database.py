"""Generate database session"""

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from what_to_do.core.settings import get_settings


@lru_cache
def get_engine() -> Engine:
    settings = get_settings()
    return create_engine(settings.db_url)


def get_db() -> Generator[Session]:
    engine = get_engine()
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
