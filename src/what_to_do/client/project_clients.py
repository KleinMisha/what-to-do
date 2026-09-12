"""Clients for Project resource."""

from typing import Protocol
from uuid import UUID

from what_to_do.client.local_client import CRUDService, LocalClient
from what_to_do.tasks.models import Project, Task


class ProjectService(CRUDService[Project], Protocol):
    """Methods the client defined below expects to be present."""

    def assign_to_new_group(self, project: Project, *, group_id: UUID) -> Project: ...
    def list_tasks(self, project_id: UUID) -> list[Task]: ...


class LocalProjectClient(LocalClient[Project]):
    """Local client exposing Project-related operations."""

    def __init__(self, service: ProjectService) -> None:
        super().__init__(service, Project)
        self.service: ProjectService = service

    def assign(self, *, project_id: UUID, group_id: UUID) -> Project:
        project = self.service.get(project_id)
        return self.service.assign_to_new_group(project, group_id=group_id)

    def list_tasks(self, id: UUID) -> list[Task]:
        return self.service.list_tasks(id)
