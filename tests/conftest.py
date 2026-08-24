from collections.abc import Generator
from uuid import uuid4

import pytest
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session, sessionmaker

from what_to_do.db.schema import Base
from what_to_do.tasks.models import Group, Project, Task

# Used in several unit tests


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
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autoflush=False, bind=engine)


@pytest.fixture
def db_session() -> Generator[Session]:
    """
    Connect to a test database.
    ----
    Test database is in-memory SQLite database
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
