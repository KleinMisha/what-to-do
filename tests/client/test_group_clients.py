"""Unit tests for the local Group client."""

from uuid import UUID, uuid4

import pytest

from tests.client.fakes import FakeLocalService
from what_to_do.client.group_clients import LocalGroupClient
from what_to_do.tasks.models import Group, Project, Task


class FakeGroupService(FakeLocalService[Group]):
    """Extends the in-memory service with project-specific operations."""

    def list_tasks(self, group_id: UUID) -> list[Task]:
        return []

    def list_projects(self, group_id: UUID) -> list[Project]:
        return []


@pytest.fixture
def client() -> LocalGroupClient:
    return LocalGroupClient(service=FakeGroupService())


def test_list_tasks(client: LocalGroupClient) -> None:
    """No meaningful client behavior; just cover the delegation."""
    group_id = uuid4()

    assert client.list_tasks(group_id) == []


def test_list_projects(client: LocalGroupClient) -> None:
    """No meaningful client behavior; just cover the delegation."""
    group_id = uuid4()

    assert client.list_projects(group_id) == []
