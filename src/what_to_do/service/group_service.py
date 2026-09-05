"""Orchestration of Group resource"""

from typing import Protocol
from uuid import UUID

from what_to_do.core.exceptions import ResourceNotFoundError
from what_to_do.service.repository import Repository
from what_to_do.tasks.models import Group, Project, Task


class TaskRepository(Repository[Task], Protocol):
    """
    Contract with additional methods this service needs to know of
    """

    def get_by_group_id(self, group_id: UUID) -> list[Task]: ...


class ProjectRepository(Repository[Project], Protocol):
    """
    Contract with additional methods this service needs to know of
    """

    def get_by_group_id(self, group_id: UUID) -> list[Project]: ...


class GroupService:
    """Group orchestration"""

    def __init__(
        self,
        tasks: TaskRepository,
        projects: ProjectRepository,
        groups: Repository[Group],
    ) -> None:
        self.tasks = tasks
        self.projects = projects
        self.groups = groups

    def create(self, group: Group) -> Group:
        """Create a new group"""
        return self.groups.create(group)

    def get(self, id: UUID) -> Group:
        """Retrieve the Group by id."""
        return self._get_or_raise(id)

    def delete(self, id: UUID) -> Group:
        """Delete group and all of it's projects and tasks"""

        # deal with the projects in this group
        for project in self.projects.get_by_group_id(id):
            self.projects.delete(project.id)

        # deal with the tasks in this group
        for task in self.tasks.get_by_group_id(id):
            self.tasks.delete(task.id)

        # delete the group itself
        group = self.groups.delete(id)
        if group is None:
            raise ResourceNotFoundError("group", id)
        return group

    def update_info(self, group: Group) -> Group:
        """Update group info"""
        # ensure group exist
        self._get_or_raise(group.id)
        after_update = self.groups.update(group)
        assert after_update is not None
        return after_update

    def list_tasks(self, group_id: UUID) -> list[Task]:
        """List all tasks assigned to a given group"""
        # ensure group exists
        self._get_or_raise(group_id)
        return self.tasks.get_by_group_id(group_id)

    def list_projects(self, group_id: UUID) -> list[Project]:
        """List all projects assigned to a given group"""
        # ensure project exists
        self._get_or_raise(group_id)
        return self.projects.get_by_group_id(group_id)

    def get_all(self) -> list[Group]:
        """Fetch all groups stored in the repository"""
        return self.groups.get_all()

    def _get_or_raise(self, id: UUID) -> Group:
        """Retrieve group from repository or raise if it does not exist."""
        group = self.groups.get(id)
        if group is None:
            raise ResourceNotFoundError("group", id)
        return group
