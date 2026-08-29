"""Unit tests for src/what_to_do/db/task_repository.py"""

from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from what_to_do.db.schema import Base
from what_to_do.db.task_repository import TaskRepository
from what_to_do.tasks.models import Priority, Task


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


def test_create_task(db_session: Session, mock_task: Task) -> None:
    """Create a new Task model and place it in the database."""
    repo = TaskRepository(db_session)
    record_in_db = repo.create(mock_task)
    assert isinstance(record_in_db, Task)
    assert record_in_db == mock_task


def test_get_task_by_id(db_session: Session, mock_task: Task) -> None:
    """Create a new Task, then grab it from db."""
    repo = TaskRepository(db_session)
    expected_task = repo.create(mock_task)
    task_found = repo.get(mock_task.id)
    assert isinstance(task_found, Task)
    assert task_found == expected_task


def test_get_unknown_game(db_session: Session, mock_task: Task) -> None:
    """Should return None if ID does not match anything in database

    NOTE with an empty database, as is the case in this test, any id is a valid test case
    """
    unknown_id = uuid4()
    repo = TaskRepository(db_session)
    task_found = repo.get(unknown_id)
    assert task_found is None

    # For good measures, create an actual entry, but attempt to retrieve using the wrong id.
    wrong_id = uuid4()
    repo.create(mock_task)
    task_found = repo.get(wrong_id)
    assert task_found is None


def test_update_task(db_session: Session, mock_task: Task) -> None:
    """Update a record created earlier."""

    # place original in datable
    repo = TaskRepository(db_session)
    repo.create(mock_task)

    # perform update
    expected = Task(
        id=mock_task.id,
        group_id=uuid4(),
        title="Update",
        description="Updated values",
        project_id=uuid4(),
        priority=Priority.LOW,
    )
    repo.update(expected)

    # fetch back from database and check
    actual = repo.get(mock_task.id)
    assert actual is not None
    assert actual == expected


def test_consecutive_task_updates(db_session: Session, mock_task: Task) -> None:
    """Make sure we can make multiple updates safely and things overwrite when expected."""
    # place original in datable
    repo = TaskRepository(db_session)
    repo.create(mock_task)

    # first update
    first_update = Task(
        id=mock_task.id,
        group_id=uuid4(),
        title="First Update",
        description="after the first update.",
        project_id=uuid4(),
        priority=Priority.LOW,
    )
    repo.update(first_update)

    # second update
    expected = Task(
        id=mock_task.id,
        group_id=uuid4(),
        title="Second Update",
        description="after two consecutive updates.",
        project_id=uuid4(),
        priority=Priority.LOW,
    )
    repo.update(expected)

    # fetch back from database and check
    actual = repo.get(mock_task.id)
    assert actual is not None
    assert actual == expected


def test_attempt_update_unknown_task(db_session: Session) -> None:
    """Attempt to update a non-existing record."""
    unknown_id = uuid4()
    # perform update
    with_unknown_id = Task(
        id=unknown_id,
        group_id=uuid4(),
        title="Update",
        description="Updated values",
        project_id=uuid4(),
        priority=Priority.LOW,
    )
    repo = TaskRepository(db_session)
    data_updated = repo.update(with_unknown_id)
    assert data_updated is None


def test_delete_task(db_session: Session, mock_task: Task) -> None:
    """Remove created record from database."""
    # Place a task
    repo = TaskRepository(db_session)
    repo.create(mock_task)

    # Delete it
    repo.delete(mock_task.id)

    # Should be unable to find it back in db
    found_data = repo.get(mock_task.id)
    assert found_data is None


def test_attempt_delete_unknown_task(db_session: Session) -> None:
    """Attempt to delete a non-existing record."""
    unknown_id = uuid4()
    repo = TaskRepository(db_session)
    deleted_data = repo.delete(unknown_id)
    assert deleted_data is None


def test_get_all_tasks(db_session: Session) -> None:
    """Place two tasks in database, check that both are returned"""
    item_1 = Task(
        id=uuid4(),
        group_id=uuid4(),
        title="One",
        description="First entry",
    )
    item_2 = Task(
        id=uuid4(),
        group_id=uuid4(),
        title="Two",
        description="Second entry",
    )
    repo = TaskRepository(db_session)
    repo.create(item_1)
    repo.create(item_2)
    items = repo.get_all()
    assert items == [item_1, item_2]


def test_get_empty_task_list(db_session: Session) -> None:
    """An empty list should get returned if no task is entered into database yet."""
    repo = TaskRepository(db_session)
    items = repo.get_all()
    assert items == []
