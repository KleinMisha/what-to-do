"""Generate database session"""

from collections.abc import Generator
from contextlib import contextmanager
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker


@lru_cache
def get_engine(db_url: str) -> Engine:
    return create_engine(db_url)


@contextmanager
def db_session(db_url: str) -> Generator[Session]:
    engine = get_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db(db_url: str) -> Generator[Session]:
    """For FastAPI dependency injection"""
    with db_session(db_url) as db:
        yield db
