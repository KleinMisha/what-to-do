"""Unit tests for src/what_to_do/service/project_service.py"""

from uuid import UUID, uuid4

import pytest

from tests.service.fake_repository import FakeRepository
from what_to_do.core.exceptions import ResourceNotFoundError
from what_to_do.service.project_service import ProjectService
from what_to_do.tasks.models import Group, Project, Task


class FakeTaskRepository(FakeRepository[Task]):
    """Implement additional method expected by service."""

    def get_by_project_id(self, project_id: UUID) -> list[Task]:
        return [task for task in self.items if task.project_id == project_id]


@pytest.fixture
def service_w_group(mock_project: Task) -> ProjectService:
    """Setup service in a valid state."""
    return ProjectService(
        tasks=FakeTaskRepository(),
        projects=FakeRepository[Project](),
        groups=FakeRepository[Group](
            [Group(id=mock_project.group_id, name="mock task's group.")]
        ),
    )


def test_create_new_project(
    service_w_group: ProjectService, mock_project: Project
) -> None:
    """Create a valid new Project."""
    created_project = service_w_group.create(mock_project)
    project_in_repo = service_w_group.get(created_project.id)
    assert created_project == project_in_repo


def test_create_project_before_group(mock_project: Project) -> None:
    """Cannot create a project before the group it belongs to is created first."""
    service = ProjectService(
        tasks=FakeTaskRepository(),
        projects=FakeRepository[Project](),
        groups=FakeRepository[Group](),
    )
    with pytest.raises(ResourceNotFoundError):
        service.create(mock_project)


def test_get_project(service_w_group: ProjectService, mock_project: Project):
    """simple roundtrip."""
    service_w_group.create(mock_project)
    found_project = service_w_group.get(mock_project.id)
    assert found_project == mock_project


def test_get_unknown_project(service_w_group: ProjectService) -> None:
    """Cannot get a project that does not exist."""
    with pytest.raises(ResourceNotFoundError):
        unknown_id = uuid4()
        service_w_group.get(unknown_id)


def test_delete_project_and_tasks(
    mock_project: Project,
    mock_task: Task,
    mock_group: Group,
) -> None:
    """Delete a previously created task + all tasks in it"""

    # assign things to the same group and project
    mock_task.group_id = mock_group.id
    mock_task.project_id = mock_project.id
    mock_project.group_id = mock_group.id

    tasks = FakeTaskRepository([mock_task])
    projects = FakeRepository[Project]()
    groups = FakeRepository[Group]([mock_group])

    service = ProjectService(
        tasks=tasks,
        projects=projects,
        groups=groups,
    )

    existing_project = service.create(mock_project)
    removed_project = service.delete(existing_project.id, keep_tasks=False)
    assert removed_project is not None
    assert removed_project == existing_project

    with pytest.raises(ResourceNotFoundError):
        service.get(removed_project.id)

    remaining_task = tasks.get(mock_task.id)
    assert remaining_task is None


def test_delete_project_keep_tasks(
    mock_project: Project,
    mock_task: Task,
    mock_group: Group,
) -> None:
    """Delete the project, but keep the tasks (just unassign from the project)"""
    # assign things to the same group and project
    mock_task.group_id = mock_group.id
    mock_task.project_id = mock_project.id
    mock_project.group_id = mock_group.id
    tasks = FakeTaskRepository([mock_task])
    projects = FakeRepository[Project]()
    groups = FakeRepository[Group]([mock_group])

    service = ProjectService(
        tasks=tasks,
        projects=projects,
        groups=groups,
    )
    existing_project = service.create(mock_project)
    removed_project = service.delete(existing_project.id, keep_tasks=True)
    assert removed_project is not None
    assert removed_project == existing_project
    with pytest.raises(ResourceNotFoundError):
        service.get(removed_project.id)

    remaining_task = tasks.get(mock_task.id)
    assert remaining_task is not None
    assert remaining_task.project_id is None
    assert remaining_task.group_id == mock_group.id
    assert remaining_task == mock_task


def test_delete_unknown_project(service_w_group: ProjectService) -> None:
    """Cannot delete a project that does not exist."""
    with pytest.raises(ResourceNotFoundError):
        unknown_id = uuid4()
        service_w_group.delete(unknown_id)


@pytest.mark.parametrize(
    ("field", "updated_value"),
    [
        ("name", "Updated title"),
        ("description", "Updated description."),
    ],
)
def test_update_project_info(
    service_w_group: ProjectService,
    mock_project: Project,
    field: str,
    updated_value: object,
) -> None:
    """Update the task description or other data."""
    # place task in repository
    service_w_group.create(mock_project)

    # change info
    setattr(mock_project, field, updated_value)

    # perform update and check persisted data carries the update.
    service_w_group.update_info(mock_project)
    persisted_project = service_w_group.get(mock_project.id)
    assert getattr(persisted_project, field) == updated_value


def test_update_unknown_project(
    service_w_group: ProjectService, mock_project: Project
) -> None:
    """Cannot update project that does not exist."""
    with pytest.raises(ResourceNotFoundError):
        service_w_group.update_info(mock_project)


def test_move_group(
    mock_project: Project,
    mock_task: Task,
) -> None:
    """Move a Project + all its tasks into a new group."""
    old_group = Group(id=mock_project.group_id, name="before")
    new_group = Group(id=uuid4(), name="after")

    mock_task.group_id = old_group.id
    mock_task.project_id = mock_project.id

    tasks = FakeTaskRepository([mock_task])
    projects = FakeRepository[Project]([mock_project])
    groups = FakeRepository[Group]([old_group, new_group])

    service = ProjectService(
        tasks=tasks,
        projects=projects,
        groups=groups,
    )

    updated_project = service.assign_to_new_group(
        mock_project,
        group_id=new_group.id,
    )

    persisted_project = service.get(mock_project.id)
    persisted_task = tasks.get(mock_task.id)

    assert updated_project.group_id == new_group.id
    assert persisted_project.group_id == new_group.id
    assert persisted_task is not None
    assert persisted_task.group_id == new_group.id


def test_move_to_unknown_group(
    service_w_group: ProjectService, mock_project: Project
) -> None:
    """Cannot move into a non-existing group."""

    unknown_id = uuid4()
    service_w_group.create(mock_project)
    with pytest.raises(ResourceNotFoundError):
        service_w_group.assign_to_new_group(mock_project, group_id=unknown_id)


def test_cannot_mutate_unknown_project(
    service_w_group: ProjectService, mock_project: Project
) -> None:
    """Must create the Task before it can be mutated (either change group/project assignments or attempt info update)."""
    with pytest.raises(ResourceNotFoundError):
        service_w_group.assign_to_new_group(
            mock_project,
            group_id=mock_project.group_id,
        )
    mock_project.description = "Updated description"
    with pytest.raises(ResourceNotFoundError):
        service_w_group.update_info(mock_project)


def test_list_tasks(
    mock_task: Task,
    mock_project: Project,
    mock_group: Group,
) -> None:
    """Correctly return all tasks in the project."""
    mock_project.group_id = mock_group.id
    mock_task.group_id = mock_group.id
    mock_task.project_id = mock_project.id

    tasks = FakeTaskRepository([mock_task])
    projects = FakeRepository[Project]([mock_project])
    groups = FakeRepository[Group]([mock_group])

    service = ProjectService(
        tasks=tasks,
        projects=projects,
        groups=groups,
    )

    result = service.list_tasks(mock_project.id)
    assert result == [mock_task]


def test_list_tasks_empty(
    mock_project: Project,
    mock_group: Group,
) -> None:
    """Return an empty list when the project has no tasks."""
    mock_project.group_id = mock_group.id

    service = ProjectService(
        tasks=FakeTaskRepository(),
        projects=FakeRepository[Project]([mock_project]),
        groups=FakeRepository[Group]([mock_group]),
    )
    result = service.list_tasks(mock_project.id)
    assert result == []
