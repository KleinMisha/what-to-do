"""Orchestration for Project resource."""

from uuid import UUID

from what_to_do.core.exceptions import InvalidAssignmentError, ResourceNotFoundError
from what_to_do.service.repository import Repository
from what_to_do.tasks.models import Group, Project, Task


class ProjectService:
    """Project orchestration."""

    def __init__(
        self,
        tasks: Repository[Task],
        projects: Repository[Project],
        groups: Repository[Group],
    ) -> None:
        self.tasks = tasks
        self.projects = projects
        self.groups = groups

    def create(self, project: Project) -> Project:
        """Create a new project"""

    def get(self, id: UUID) -> Project:
        """Retrieve the Project by id."""
        project = self.projects.get(id)
        if project is None:
            raise ResourceNotFoundError("project", id)
        return project

    def delete(self, id: UUID, keep_tasks: bool = False) -> Project:
        """Remove a project.

        What to do with the underlying tasks?
            if keep_tasks ---> keep the tasks and unassign them from the current project and remain in their respective group.
            if keep_tasks=False (default) ---> also remove the tasks within this project
        """
        project = self.projects.delete(id)
        if project is None:
            raise ResourceNotFoundError("project", id)
        return project

    def update_info(self, project: Project) -> Project:
        """Update project info"""

    def assign_to_new_group(self, project: Project, *, group_id: UUID) -> Project:
        """Assign a project, and all its tasks, to a new group."""
        # assure project exists
        self._get_or_raise(project.id)

    def _get_or_raise(self, id: UUID) -> Project:
        """Retrieve project from repository or raise if it does not exist."""
        project = self.projects.get(id)
        if project is None:
            raise ResourceNotFoundError("project", id)
        return project

    def _validate_assignment(self) -> None:
        """Check that project exists"""

    def list_tasks(self, project_id: UUID) -> list[Task]:
        """List all tasks belonging to a given project ID"""
        tasks: list[Task] = []
        for 