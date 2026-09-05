from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine, StaticPool, create_engine
from sqlalchemy.orm import Session, sessionmaker

from what_to_do.api.server import app
from what_to_do.core.settings import get_settings
from what_to_do.db.database import get_db
from what_to_do.db.schema import Base
from what_to_do.tasks.models import Group, Project, Task


@pytest.fixture()
def mock_task() -> Task:
    return Task(
        id=uuid4(),
        group_id=uuid4(),
        title="Mock task",
        description="This is a mock task that is super duper important. ",
    )


@pytest.fixture()
def mock_project() -> Project:
    return Project(
        id=uuid4(),
        group_id=uuid4(),
        name="Mock",
        description="This is a mock project.",
    )


@pytest.fixture()
def mock_group() -> Group:
    return Group(id=uuid4(), name="Mock")


# Setup an in-memory SQLite database for testing
@pytest.fixture
def db_engine() -> Generator[Engine]:
    engine = create_engine(
        url="sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def db_session(db_engine: Engine) -> Generator[Session]:
    """
    Connect to a test database.
    ----
    Test database is in-memory SQLite database
    """
    session_factory = sessionmaker(autoflush=False, bind=db_engine)
    session = session_factory()

    try:
        yield session
    finally:
        session.close()


# test app client with overwrites for database connections
@pytest.fixture
def client(db_session: Session) -> Generator[TestClient]:
    """Overwrite connections to database, while otherwise using the production application."""

    # Overwrite db session with the test session
    # NOTE all services in endpoints are already made to depend on get_db.
    # Hence, FastAPI should be able to take care of spinning up the
    # full application with this single override
    def _override_get_db() -> Generator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    # Prevent the production lifespan from creating tables on the
    # production engine during tests
    @asynccontextmanager
    async def _override_lifespan(_: FastAPI) -> AsyncGenerator[None]:
        yield

    original_lifespan = app.router.lifespan_context
    app.router.lifespan_context = _override_lifespan

    # spin up client
    try:
        with TestClient(app) as client:
            yield client

    # Cleanup --> set back to original
    finally:
        app.router.lifespan_context = original_lifespan
        app.dependency_overrides.clear()
