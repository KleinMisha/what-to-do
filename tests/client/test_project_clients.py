"""Unit tests for the local Project client."""

from uuid import UUID, uuid4

import pytest

from tests.client.fakes import FakeLocalService
from what_to_do.client.project_clients import LocalProjectClient
from what_to_do.tasks.models import Project, Task


class FakeProjectService(FakeLocalService[Project]):
    """Extends the in-memory service with project-specific operations."""

    def assign_to_new_group(
        self,
        project: Project,
        *,
        group_id: UUID,
    ) -> Project:
        project.group_id = group_id
        return project

    def list_tasks(self, project_id: UUID) -> list[Task]:
        return []

    def delete(self, id: UUID, keep_tasks: bool = False) -> Project:
        return super().delete(id)


@pytest.fixture
def client() -> LocalProjectClient:
    return LocalProjectClient(service=FakeProjectService())


def test_assign_to_new_group(client: LocalProjectClient) -> None:
    """Assign the project to a new group."""
    project_id = uuid4()
    before_group = uuid4()
    after_group = uuid4()

    client.create(
        id=project_id,
        group_id=before_group,
        name="Test",
        description="just to test",
    )

    updated = client.assign(
        project_id=project_id,
        group_id=after_group,
    )

    assert updated == Project(
        id=project_id,
        group_id=after_group,
        name="Test",
        description="just to test",
    )


def test_list_tasks(client: LocalProjectClient) -> None:
    """No meaningful client behavior; just cover the delegation."""
    project_id = uuid4()

    assert client.list_tasks(project_id) == []
