"""Unit tests for /src/what_to_do/service/task_service.py"""

from uuid import UUID, uuid4

import pytest

from what_to_do.core.exceptions import InvalidAssignmentError, ResourceNotFoundError
from what_to_do.service.task_service import TaskService
from what_to_do.tasks.models import Group, HasID, Priority, Project, Task


class FakeRepository[T: HasID]:
    """Repository that stores items in-memory in a simple list"""

    def __init__(self, items: list[T] | None = None) -> None:
        self.items = items or []

    def create(self, model: T) -> T:
        self.items.append(model)
        return model

    def get(self, id: UUID) -> T | None:
        return next(
            (item for item in self.items if item.id == id),
            None,
        )

    def delete(self, id: UUID) -> T | None:
        existing_resource = self.get(id)
        if existing_resource is None:
            return None
        self.items.remove(existing_resource)
        return existing_resource

    def update(self, model: T) -> T | None:
        existing_resource = self.get(model.id)
        if existing_resource is None:
            return None
        idx = self.items.index(existing_resource)
        self.items[idx] = model
        return model


@pytest.fixture
def service_w_group(mock_task: Task) -> TaskService:
    """Setup task service in a valid state."""
    return TaskService(
        tasks=FakeRepository[Task](),
        projects=FakeRepository[Project](),
        groups=FakeRepository[Group](
            [Group(id=mock_task.group_id, name="mock task's group.")]
        ),
    )


@pytest.fixture
def service_w_invalid_assignment(
    mock_task: Task,
) -> tuple[TaskService, Task]:
    """Setup a task service with an inconsistent task/project assignment (inconsistent group IDs)"""

    # Create a project assigned to a group different from the group the task is assigned to
    project = Project(
        id=uuid4(),
        group_id=uuid4(),
        name="Mock project",
    )

    # Now assign the task to this project anyways. (Meaning the task is now part of two groups, which is an invalid state.)
    mock_task.project_id = project.id

    service = TaskService(
        tasks=FakeRepository(),
        projects=FakeRepository([project]),
        groups=FakeRepository([Group(id=mock_task.group_id, name="Mock group")]),
    )
    return service, mock_task


def test_create_new_task(service_w_group: TaskService, mock_task: Task) -> None:
    """Create a valid new Task."""
    # create the group first
    created_task = service_w_group.create(mock_task)
    task_in_repo = service_w_group.get(created_task.id)
    assert created_task == task_in_repo


def test_create_task_before_group(mock_task: Task) -> None:
    """Cannot create a task before the group it belongs to is created first."""
    service = TaskService(
        tasks=FakeRepository[Task](),
        projects=FakeRepository[Project](),
        groups=FakeRepository[Group](),
    )
    with pytest.raises(InvalidAssignmentError):
        service.create(mock_task)


def test_create_task_before_project(
    service_w_group: TaskService, mock_task: Task
) -> None:
    """Cannot create a task before the project it belongs to is created first."""
    unknown_id = uuid4()
    mock_task.project_id = unknown_id
    with pytest.raises(InvalidAssignmentError):
        service_w_group.create(mock_task)


def test_create_with_invalid_assignment(
    service_w_invalid_assignment: tuple[TaskService, Task],
) -> None:
    """Both project and group exist, but have inconsistent assignments."""
    service, task = service_w_invalid_assignment

    with pytest.raises(InvalidAssignmentError):
        service.create(task)


def test_get_task(service_w_group: TaskService, mock_task: Task):
    """simple roundtrip."""
    service_w_group.create(mock_task)
    found_task = service_w_group.get(mock_task.id)
    assert found_task == mock_task


def test_get_unknown_task(service_w_group: TaskService) -> None:
    """Cannot get a task that does not exist."""
    with pytest.raises(ResourceNotFoundError):
        unknown_id = uuid4()
        service_w_group.get(unknown_id)


def test_delete_task(service_w_group: TaskService, mock_task: Task) -> None:
    """Delete a previously created task"""
    existing_task = service_w_group.create(mock_task)
    removed_task = service_w_group.delete(existing_task.id)
    assert removed_task is not None
    assert removed_task == existing_task


def test_delete_unknown_task(service_w_group: TaskService) -> None:
    """Cannot delete a task that does not exist."""
    with pytest.raises(ResourceNotFoundError):
        unknown_id = uuid4()
        service_w_group.delete(unknown_id)


@pytest.mark.parametrize(
    ("field", "updated_value"),
    [
        ("title", "Updated title"),
        ("description", "Updated description."),
        ("priority", Priority.LOW),
        ("priority", Priority.HIGH),
    ],
)
def test_update_task_info(
    service_w_group: TaskService,
    mock_task: Task,
    field: str,
    updated_value: object,
) -> None:
    """Update the task description or other data."""
    # place task in repository
    service_w_group.create(mock_task)

    # change info
    setattr(mock_task, field, updated_value)

    # perform update and check persisted data carries the update.
    service_w_group.update_info(mock_task)
    persisted_task = service_w_group.get(mock_task.id)
    assert getattr(persisted_task, field) == updated_value


def test_update_unknown_task(service_w_group: TaskService, mock_task: Task) -> None:
    """Cannot update task that does not exist."""
    with pytest.raises(ResourceNotFoundError):
        service_w_group.update_info(mock_task)


def test_attempt_invalid_update(
    service_w_invalid_assignment: tuple[TaskService, Task],
) -> None:
    """
    Cannot adjust group_id / project_id in inconsistent manners

    NOTE Even if this is not the intended usage of this .update_info() method, nothing is preventing from doing so.
    """
    service, task = service_w_invalid_assignment
    with pytest.raises(InvalidAssignmentError):
        service.update_info(task)


def test_move_group(mock_task: Task) -> None:
    """Move individual task into a new group."""

    # setup service with the required groups, projects and task(s)
    old_group = Group(id=mock_task.group_id, name="before")
    new_group = Group(id=uuid4(), name="after")
    service = TaskService(
        tasks=FakeRepository[Task](),
        projects=FakeRepository[Project](),
        groups=FakeRepository[Group]([old_group, new_group]),
    )
    service.create(mock_task)

    # assign to a new group and check persisted data carries the update.
    updated_task = service.assign(mock_task, group_id=new_group.id, project_id=None)
    persisted_task = service.get(mock_task.id)
    assert updated_task.group_id == new_group.id
    assert persisted_task.group_id == new_group.id


def test_move_project_in_same_group(mock_task: Task) -> None:
    """Move individual task into a new project, within the same group."""

    # setup service with the required groups, projects and task(s)
    current_group = Group(id=mock_task.group_id, name="shared group")
    old_project = Project(id=uuid4(), group_id=mock_task.group_id, name="before")
    new_project = Project(id=uuid4(), group_id=mock_task.group_id, name="after")

    service = TaskService(
        tasks=FakeRepository[Task](),
        projects=FakeRepository[Project]([old_project, new_project]),
        groups=FakeRepository[Group]([current_group]),
    )
    mock_task.project_id = old_project.id
    service.create(mock_task)

    # assign to a new group and check persisted data carries the update.
    updated_task = service.assign(
        mock_task, group_id=mock_task.group_id, project_id=new_project.id
    )
    persisted_task = service.get(mock_task.id)
    assert updated_task.project_id == new_project.id
    assert persisted_task.project_id == new_project.id


def test_move_to_unknown_group(service_w_group: TaskService, mock_task: Task) -> None:
    """Cannot move into a non-existing group."""

    unknown_id = uuid4()
    service_w_group.create(mock_task)
    with pytest.raises(ResourceNotFoundError):
        service_w_group.assign(mock_task, group_id=unknown_id, project_id=None)


def test_move_to_unknown_project(service_w_group: TaskService, mock_task: Task) -> None:
    """Cannot move into a non-existing project."""

    unknown_id = uuid4()
    service_w_group.create(mock_task)
    with pytest.raises(ResourceNotFoundError):
        service_w_group.assign(
            mock_task, group_id=mock_task.group_id, project_id=unknown_id
        )


def test_inconsistent_assignment(mock_task: Task) -> None:
    """Cannot assign to an inconsistent state."""

    # setup service with the required groups, projects and task(s)
    group = Group(id=mock_task.group_id, name="group A")
    project = Project(id=uuid4(), group_id=uuid4(), name="project in group B")

    service = TaskService(
        tasks=FakeRepository[Task](),
        projects=FakeRepository[Project]([project]),
        groups=FakeRepository[Group]([group]),
    )
    service.create(mock_task)

    # attempt assignment
    with pytest.raises(InvalidAssignmentError):
        service.assign(mock_task, group_id=group.id, project_id=project.id)


def test_unassign_project(mock_task: Task) -> None:
    """Unassign the project, stay within the same group."""
    # setup service with the required groups, projects and task(s)
    current_group = Group(id=mock_task.group_id, name="shared group")
    current_project = Project(id=uuid4(), group_id=mock_task.group_id, name="before")

    service = TaskService(
        tasks=FakeRepository[Task](),
        projects=FakeRepository[Project]([current_project]),
        groups=FakeRepository[Group]([current_group]),
    )
    mock_task.project_id = current_project.id
    service.create(mock_task)

    # assign to a new group and check persisted data carries the update.
    updated_task = service.unassign_project(mock_task)
    persisted_task = service.get(mock_task.id)
    assert updated_task.project_id == None
    assert persisted_task.project_id == None


def test_cannot_mutate_unknown_task(
    service_w_group: TaskService, mock_task: Task
) -> None:
    """Must create the Task before it can be mutated (either change group/project assignments or attempt info update)."""
    with pytest.raises(ResourceNotFoundError):
        service_w_group.assign(
            mock_task, group_id=mock_task.group_id, project_id=mock_task.project_id
        )

    with pytest.raises(ResourceNotFoundError):
        service_w_group.unassign_project(mock_task)

    mock_task.description = "Updated description"
    with pytest.raises(ResourceNotFoundError):
        service_w_group.update_info(mock_task)
