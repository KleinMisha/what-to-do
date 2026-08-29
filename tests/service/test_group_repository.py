"""Unit tests for src/what_to_do/service/group_service.py"""

from uuid import UUID, uuid4

import pytest

from tests.service.fake_repository import FakeRepository
from what_to_do.core.exceptions import ResourceNotFoundError
from what_to_do.service.group_service import GroupService
from what_to_do.tasks.models import Group, HasGroupID, Project, Task


class FakeRepositoryWithGroupSearch[T: HasGroupID](FakeRepository[T]):
    """Implement additional method expected by service."""

    def get_by_group_id(self, group_id: UUID) -> list[T]:
        return [item for item in self.items if item.group_id == group_id]


@pytest.fixture
def group_service() -> GroupService:
    """set up a service in a valid state. A basic service with no groups (hence, no tasks or projects) in it yet."""
    return GroupService(
        tasks=FakeRepositoryWithGroupSearch[Task](),
        projects=FakeRepositoryWithGroupSearch[Project](),
        groups=FakeRepository[Group](),
    )


def test_create_new_group(group_service: GroupService, mock_group: Group) -> None:
    """Create a valid new Project."""
    created_group = group_service.create(mock_group)
    group_in_repo = group_service.get(created_group.id)
    assert created_group == group_in_repo


def test_get_group(group_service: GroupService, mock_group: Group) -> None:
    """simple roundtrip."""
    group_service.create(mock_group)
    found_group = group_service.get(mock_group.id)
    assert found_group == mock_group


def test_get_unknown_group(group_service: GroupService) -> None:
    """Cannot get a group that does not exist."""
    with pytest.raises(ResourceNotFoundError):
        unknown_id = uuid4()
        group_service.get(unknown_id)


def test_delete_group_and_child_resources(
    mock_group: Group,
    mock_project: Project,
    mock_task: Task,
) -> None:
    """Delete a previously created group + all projects/tasks in it"""

    # assign things to the same group
    mock_project.group_id = mock_group.id
    mock_task.project_id = mock_project.id
    mock_task.group_id = mock_group.id

    tasks = FakeRepositoryWithGroupSearch[Task]([mock_task])
    projects = FakeRepositoryWithGroupSearch[Project]([mock_project])
    groups = FakeRepository[Group]()
    service = GroupService(
        tasks=tasks,
        projects=projects,
        groups=groups,
    )

    existing_group = service.create(mock_group)
    removed_group = service.delete(existing_group.id)
    assert removed_group is not None
    assert removed_group == existing_group

    with pytest.raises(ResourceNotFoundError):
        service.get(removed_group.id)

    remaining_project = projects.get(mock_project.id)
    assert remaining_project is None

    remaining_task = tasks.get(mock_task.id)
    assert remaining_task is None


def test_delete_unknown_group(group_service: GroupService) -> None:
    """Cannot delete a project that does not exist."""
    with pytest.raises(ResourceNotFoundError):
        unknown_id = uuid4()
        group_service.delete(unknown_id)


@pytest.mark.parametrize(
    ("field", "updated_value"),
    [
        ("name", "Updated title"),
    ],
)
def test_update_group_info(
    group_service: GroupService, mock_group: Group, field: str, updated_value: object
) -> None:
    """Update a Group's information."""
    # place group in repository
    group_service.create(mock_group)

    # change info
    setattr(mock_group, field, updated_value)

    # perform update and check persisted data carries the update
    group_service.update_info(mock_group)
    persisted_group = group_service.get(mock_group.id)
    assert getattr(persisted_group, field) == updated_value


def test_cannot_mutate_unknown_group(
    group_service: GroupService, mock_group: Group
) -> None:
    """Cannot update a non-existing resource."""
    mock_group.name = "Updated name"
    with pytest.raises(ResourceNotFoundError):
        group_service.update_info(mock_group)


def test_list_tasks(
    mock_task: Task,
    mock_project: Project,
    mock_group: Group,
) -> None:
    """Correctly return all tasks in the group."""
    mock_project.group_id = mock_group.id
    mock_task.group_id = mock_group.id
    mock_task.project_id = mock_project.id

    tasks = FakeRepositoryWithGroupSearch[Task]([mock_task])
    projects = FakeRepositoryWithGroupSearch[Project]([mock_project])
    groups = FakeRepository[Group]([mock_group])

    service = GroupService(
        tasks=tasks,
        projects=projects,
        groups=groups,
    )

    result = service.list_tasks(mock_group.id)
    assert result == [mock_task]


def test_list_tasks_empty(
    mock_project: Project,
    mock_group: Group,
) -> None:
    """Return an empty list when the group has no tasks."""
    mock_project.group_id = mock_group.id

    tasks = FakeRepositoryWithGroupSearch[Task]()
    projects = FakeRepositoryWithGroupSearch[Project]([mock_project])
    groups = FakeRepository[Group]([mock_group])

    service = GroupService(
        tasks=tasks,
        projects=projects,
        groups=groups,
    )

    result = service.list_tasks(mock_group.id)
    assert result == []


def test_list_projects(
    mock_task: Task,
    mock_project: Project,
    mock_group: Group,
) -> None:
    """Correctly return all projects in the group."""
    mock_project.group_id = mock_group.id
    mock_task.group_id = mock_group.id
    mock_task.project_id = mock_project.id

    tasks = FakeRepositoryWithGroupSearch[Task]([mock_task])
    projects = FakeRepositoryWithGroupSearch[Project]([mock_project])
    groups = FakeRepository[Group]([mock_group])

    service = GroupService(
        tasks=tasks,
        projects=projects,
        groups=groups,
    )

    result = service.list_projects(mock_group.id)
    assert result == [mock_project]


def test_list_projects_empty(mock_group: Group, mock_task: Task) -> None:
    """Return an empty list when the group has no projects."""
    mock_task.group_id = mock_group.id
    mock_task.project_id = None

    tasks = FakeRepositoryWithGroupSearch[Task]([mock_task])
    projects = FakeRepositoryWithGroupSearch[Project]()
    groups = FakeRepository[Group]([mock_group])

    service = GroupService(
        tasks=tasks,
        projects=projects,
        groups=groups,
    )

    result = service.list_projects(mock_group.id)
    assert result == []
