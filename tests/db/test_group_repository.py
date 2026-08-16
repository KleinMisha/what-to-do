"""Unit tests for src/what_to_do/db/group_repository.py"""

from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from what_to_do.db.group_repository import GroupRepository
from what_to_do.db.schema import Base
from what_to_do.tasks.models import Group


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
def mock_group() -> Group:
    return Group(id=uuid4(), name="Mock")


def test_create_group(db_session: Session, mock_group: Group) -> None:
    """Create a new Group model and place it in the database."""
    repo = GroupRepository(db_session)
    record_in_db = repo.create(mock_group)
    assert isinstance(record_in_db, Group)
    assert record_in_db == mock_group


def test_get_group_by_id(db_session: Session, mock_group: Group) -> None:
    """Create a new Group, then grab it from db."""
    repo = GroupRepository(db_session)
    expected_group = repo.create(mock_group)
    group_found = repo.get(mock_group.id)
    assert isinstance(group_found, Group)
    assert group_found == expected_group


def test_get_unknown_game(db_session: Session, mock_group: Group) -> None:
    """Should return None if ID does not match anything in database

    NOTE with an empty database, as is the case in this test, any id is a valid test case
    """
    unknown_id = uuid4()
    repo = GroupRepository(db_session)
    group_found = repo.get(unknown_id)
    assert group_found is None

    # For good measures, create an actual entry, but attempt to retrieve using the wrong id.
    wrong_id = uuid4()
    repo.create(mock_group)
    group_found = repo.get(wrong_id)
    assert group_found is None


def test_update_group(db_session: Session, mock_group: Group) -> None:
    """Update a record created earlier."""

    # place original in datable
    repo = GroupRepository(db_session)
    repo.create(mock_group)

    # perform update
    expected = Group(
        id=mock_group.id,
        name="Update",
    )
    repo.update(expected)

    # fetch back from database and check
    actual = repo.get(mock_group.id)
    assert actual is not None
    assert actual == expected


def test_consecutive_group_updates(db_session: Session, mock_group: Group) -> None:
    """Make sure we can make multiple updates safely and things overwrite when expected."""
    # place original in datable
    repo = GroupRepository(db_session)
    repo.create(mock_group)

    # first update
    first_update = Group(
        id=mock_group.id,
        name="First Update",
    )
    repo.update(first_update)

    # second update
    expected = Group(
        id=mock_group.id,
        name="Second Update",
    )
    repo.update(expected)

    # fetch back from database and check
    actual = repo.get(mock_group.id)
    assert actual is not None
    assert actual == expected


def test_attempt_update_unknown_group(db_session: Session) -> None:
    """Attempt to update a non-existing record."""
    unknown_id = uuid4()
    # perform update
    with_unknown_id = Group(
        id=unknown_id,
        name="Update",
    )
    repo = GroupRepository(db_session)
    data_updated = repo.update(with_unknown_id)
    assert data_updated is None


def test_delete_group(db_session: Session, mock_group: Group) -> None:
    """Remove created record from database."""
    # Place a project
    repo = GroupRepository(db_session)
    repo.create(mock_group)

    # Delete it
    repo.delete(mock_group.id)

    # Should be unable to find it back in db
    found_data = repo.get(mock_group.id)
    assert found_data is None


def test_attempt_delete_unknown_group(db_session: Session) -> None:
    """Attempt to delete a non-existing record."""
    unknown_id = uuid4()
    repo = GroupRepository(db_session)
    deleted_data = repo.delete(unknown_id)
    assert deleted_data is None
