"""Orchestration for Task resource."""

from uuid import UUID

from what_to_do.core.exceptions import InvalidAssignmentError, ResourceNotFoundError
from what_to_do.service.repository import Repository
from what_to_do.tasks.models import Group, Project, Task


class TaskService:
    """Task orchestration."""

    def __init__(
        self,
        tasks: Repository[Task],
        projects: Repository[Project],
        groups: Repository[Group],
    ) -> None:
        self.tasks = tasks
        self.projects = projects
        self.groups = groups

    def create(self, task: Task) -> Task:
        """Create a new task"""
        # Check validity of assignments.
        self._validate_task_assignment(
            task_id=task.id,
            project_id=task.project_id,
            group_id=task.group_id,
        )
        return self.tasks.create(task)

    def get(self, id: UUID) -> Task:
        """Retrieve the Task by id."""
        return self._get_or_raise(id)

    def delete(self, id: UUID) -> Task:
        """Remove the entered Task."""
        task = self.tasks.delete(id)
        if task is None:
            raise ResourceNotFoundError("task", id)
        return task

    def update_info(self, task: Task) -> Task:
        """Update task info."""
        # In case project / group assignments have changed
        self._validate_task_assignment(
            task_id=task.id,
            project_id=task.project_id,
            group_id=task.group_id,
        )
        after_update = self.tasks.update(task)
        if after_update is None:
            raise ResourceNotFoundError("task", task.id)
        return after_update

    def assign(
        self,
        task: Task,
        *,
        group_id: UUID,
        project_id: UUID | None,
    ) -> Task:
        """Assign task to a new group and/or project"""
        # assure the task exists
        self._get_or_raise(task.id)
        return self._change_assignment(task, project_id=project_id, group_id=group_id)

    def unassign_project(self, task: Task) -> Task:
        """Keep the task in the same group, but unassign it from any project."""
        # assure the task exists
        self._get_or_raise(task.id)
        return self._change_assignment(task, project_id=None, group_id=task.group_id)

    def _get_or_raise(self, id: UUID) -> Task:
        """Retrieve task from repository or raise if it does not exist."""
        task = self.tasks.get(id)
        if task is None:
            raise ResourceNotFoundError("task", id)
        return task

    def _change_assignment(
        self,
        task: Task,
        *,
        project_id: UUID | None,
        group_id: UUID,
    ) -> Task:
        """Change project/group (un)assignment of the given task."""

        # Assure update is valid
        self._validate_task_assignment(
            task_id=task.id,
            project_id=project_id,
            group_id=group_id,
        )

        # Perform update
        task.project_id = project_id
        task.group_id = group_id
        after_update = self.tasks.update(task)

        # NOTE: Already used _get_or_raise() to assure the task exists.
        assert after_update is not None
        return after_update

    def _validate_task_assignment(
        self,
        *,
        task_id: UUID,
        project_id: UUID | None,
        group_id: UUID,
    ) -> None:
        """
        Validate that task assignment adheres to business logic.
        -----

        1. Ensure the intended group exists.
        2. Ensure the intended project exists.
        3. Ensure the intended project is assigned to the intended group.
        """

        # 1. Ensure the intended group exists.
        group = self.groups.get(group_id)
        if group is None:
            raise ResourceNotFoundError("group", group_id)

        if project_id is not None:
            # 2. Ensure the intended project exists.
            project = self.projects.get(project_id)
            if project is None:
                raise ResourceNotFoundError("project", project_id)

            # 3. Ensure the intended project is indeed assigned to the intended group.
            if project.group_id != group_id:
                raise InvalidAssignmentError(
                    f"Task {task_id} cannot be simultaneously assigned to project {project_id} "
                    f"in group {group_id}, because project is assigned to group "
                    f"{project.group_id}."
                )
