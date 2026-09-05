"""Orchestration for Project resource."""

from typing import Protocol
from uuid import UUID

from what_to_do.core.exceptions import ResourceNotFoundError
from what_to_do.service.repository import Repository
from what_to_do.tasks.models import Group, Project, Task


class TaskRepository(Repository[Task], Protocol):
    """
    Contract with additional methods this service needs to know of
    """

    def get_by_project_id(self, project_id: UUID) -> list[Task]: ...


class ProjectService:
    """Project orchestration."""

    def __init__(
        self,
        tasks: TaskRepository,
        projects: Repository[Project],
        groups: Repository[Group],
    ) -> None:
        self.tasks = tasks
        self.projects = projects
        self.groups = groups

    def create(self, project: Project) -> Project:
        """Create a new project"""
        self._ensure_group_exists(project.group_id)
        return self.projects.create(project)

    def get(self, id: UUID) -> Project:
        """Retrieve the Project by id."""
        return self._get_or_raise(id)

    def delete(self, id: UUID, keep_tasks: bool = False) -> Project:
        """Remove a project.

        What to do with the underlying tasks?
            if keep_tasks ---> keep the tasks and unassign them from the current project and remain in their respective group.
            if keep_tasks=False (default) ---> also remove the tasks within this project
        """
        # deal with the tasks in this group
        tasks = self.tasks.get_by_project_id(id)
        if keep_tasks:
            for task in tasks:
                task.project_id = None
                self.tasks.update(task)
        else:
            for task in tasks:
                self.tasks.delete(task.id)

        # delete the project itself
        project = self.projects.delete(id)
        if project is None:
            raise ResourceNotFoundError("project", id)
        return project

    def update_info(self, project: Project) -> Project:
        """Update project info"""
        # In case project / group assignments have changed
        # ensure both project and intended group exist
        self._get_or_raise(project.id)
        self._ensure_group_exists(project.group_id)
        after_update = self.projects.update(project)
        assert after_update is not None
        return after_update

    def assign_to_new_group(self, project: Project, *, group_id: UUID) -> Project:
        """Assign a project, and all its tasks, to a new group."""
        # ensure both project and intended group exist
        self._get_or_raise(project.id)
        self._ensure_group_exists(group_id)

        # Move all tasks
        for task in self.tasks.get_by_project_id(project.id):
            task.group_id = group_id
            self.tasks.update(task)

        # Move the project itself
        project.group_id = group_id
        after_update = self.projects.update(project)
        # NOTE: Already used _get_or_raise() to assure the project exists.
        assert after_update is not None
        return after_update

    def list_tasks(self, project_id: UUID) -> list[Task]:
        """List all tasks assigned to a given project"""
        # ensure project exists
        self._get_or_raise(project_id)
        return self.tasks.get_by_project_id(project_id)

    def get_all(self) -> list[Project]:
        """Fetch all projects stored in the repository"""
        return self.projects.get_all()

    def _get_or_raise(self, id: UUID) -> Project:
        """Retrieve project from repository or raise if it does not exist."""
        project = self.projects.get(id)
        if project is None:
            raise ResourceNotFoundError("project", id)
        return project

    def _ensure_group_exists(self, id: UUID) -> None:
        """Make sure the intended group exists."""
        group = self.groups.get(id)
        if group is None:
            raise ResourceNotFoundError("group", id)
