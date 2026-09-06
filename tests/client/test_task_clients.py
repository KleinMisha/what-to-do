"""Unit tests for src/what_to_do/client/task_clients.py

Only test the parts not included in the LocalClient[T] class with shared logic.
"""

from uuid import UUID, uuid4

import pytest

from tests.client.fakes import FakeLocalService
from what_to_do.client.task_clients import LocalTaskClient
from what_to_do.tasks.models import Task


class FakeTaskService(FakeLocalService[Task]):
    """extends the in-memory service with task-specific operations."""

    def assign(self, task: Task, *, group_id: UUID, project_id: UUID | None) -> Task:
        task.group_id = group_id
        task.project_id = project_id
        return task


@pytest.fixture
def client() -> LocalTaskClient:
    return LocalTaskClient(service=FakeTaskService())


def test_assign_to_new_group_and_project(client: LocalTaskClient) -> None:
    """Assign the task to a new group and a new project"""
    task_id = uuid4()
    before_project = uuid4()
    before_group = uuid4()
    after_project = uuid4()
    after_group = uuid4()
    client.create(
        id=task_id,
        group_id=before_group,
        project_id=before_project,
        title="Test",
        description="just to test",
    )
    updated = client.assign(
        task_id=task_id,
        project_id=after_project,
        group_id=after_group,
    )

    assert updated == Task(
        id=task_id,
        group_id=after_group,
        project_id=after_project,
        title="Test",
        description="just to test",
    )


def test_unassign_from_project(client: LocalTaskClient) -> None:
    """Setting the ID to None should work."""
    task_id = uuid4()
    before_project = uuid4()
    group_id = uuid4()
    after_project = None

    client.create(
        id=task_id,
        group_id=group_id,
        project_id=before_project,
        title="Test",
        description="just to test",
    )
    updated = client.assign(
        task_id=task_id,
        project_id=after_project,
        group_id=group_id,
    )

    assert updated == Task(
        id=task_id,
        group_id=group_id,
        project_id=None,
        title="Test",
        description="just to test",
    )
