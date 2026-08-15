"""Unit tests for src/what_to_do/db/project_repository.py"""

from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from what_to_do.db.project_repository import ProjectRepository
from what_to_do.db.schema import Base
from what_to_do.tasks.models import Project


@pytest.fixture(autouse=True)
def clear_db(db_session: Session) -> None:
    """
    Drops all tables (and creates them from scratch) between unit tests.
    Ensures unit tests all start from a clean slate that does not share data.
    """
    # Delete all tables
    Base.metadata.drop_all(db_session.get_bind())

    # Recreate / Start from scratch
    Base.metadata.create_all(db_session.get_bind())


@pytest.fixture()
def mock_project() -> Project:
    return Project(
        id=uuid4(),
        group_id=uuid4(),
        name="Mock",
        description="This is a mock project.",
    )


def test_create_project(db_session: Session, mock_project: Project) -> None:
    """Create a new Project model and place it in the database."""
    repo = ProjectRepository(db_session)
    record_in_db = repo.create(mock_project)
    assert isinstance(record_in_db, Project)
    assert record_in_db == mock_project


def test_get_project_by_id(db_session: Session, mock_project: Project) -> None:
    """Create a new Project, then grab it from db."""
    repo = ProjectRepository(db_session)
    expected_project = repo.create(mock_project)
    project_found = repo.get(mock_project.id)
    assert isinstance(project_found, Project)
    assert project_found == expected_project


def test_get_unknown_game(db_session: Session, mock_project: Project) -> None:
    """Should return None if ID does not match anything in database

    NOTE with an empty database, as is the case in this test, any id is a valid test case
    """
    unknown_id = uuid4()
    repo = ProjectRepository(db_session)
    project_found = repo.get(unknown_id)
    assert project_found is None

    # For good measures, create an actual entry, but attempt to retrieve using the wrong id.
    wrong_id = uuid4()
    repo.create(mock_project)
    project_found = repo.get(wrong_id)
    assert project_found is None


def test_update_project(db_session: Session, mock_project: Project) -> None:
    """Update a record created earlier."""

    # place original in datable
    repo = ProjectRepository(db_session)
    repo.create(mock_project)

    # perform update
    expected = Project(
        id=mock_project.id,
        group_id=uuid4(),
        name="Update",
        description="Updated values",
    )
    repo.update(expected)

    # fetch back from database and check
    actual = repo.get(mock_project.id)
    assert actual is not None
    assert actual == expected


def test_consecutive_project_updates(
    db_session: Session, mock_project: Project
) -> None:
    """Make sure we can make multiple updates safely and things overwrite when expected."""
    # place original in datable
    repo = ProjectRepository(db_session)
    repo.create(mock_project)

    # first update
    first_update = Project(
        id=mock_project.id,
        group_id=uuid4(),
        name="First Update",
        description="after the first update.",
    )
    repo.update(first_update)

    # second update
    expected = Project(
        id=mock_project.id,
        group_id=uuid4(),
        name="Second Update",
        description="after two consecutive updates.",
    )
    repo.update(expected)

    # fetch back from database and check
    actual = repo.get(mock_project.id)
    assert actual is not None
    assert actual == expected


def test_attempt_update_unknown_project(db_session: Session) -> None:
    """Attempt to update a non-existing record."""
    unknown_id = uuid4()
    # perform update
    with_unknown_id = Project(
        id=unknown_id,
        group_id=uuid4(),
        name="Update",
        description="Updated values",
    )
    repo = ProjectRepository(db_session)
    data_updated = repo.update(with_unknown_id)
    assert data_updated is None


def test_delete_project(db_session: Session, mock_project: Project) -> None:
    """Remove created record from database."""
    # Place a project
    repo = ProjectRepository(db_session)
    repo.create(mock_project)

    # Delete it
    repo.delete(mock_project.id)

    # Should be unable to find it back in db
    found_data = repo.get(mock_project.id)
    assert found_data is None


def test_attempt_delete_unknown_project(
    db_session: Session, mock_project: Project
) -> None:
    """Attempt to delete a non-existing record."""
    unknown_id = uuid4()
    repo = ProjectRepository(db_session)
    deleted_data = repo.delete(unknown_id)
    assert deleted_data is None
