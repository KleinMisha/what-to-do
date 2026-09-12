"""Clients for Project resource."""

from typing import Protocol
from uuid import UUID

from what_to_do.client.local_client import CRUDService, LocalClient
from what_to_do.tasks.models import Group, Project, Task


class GroupService(CRUDService[Group], Protocol):
    """Methods the client defined below expects to be present."""

    def list_tasks(self, group_id: UUID) -> list[Task]: ...
    def list_projects(self, group_id: UUID) -> list[Project]: ...


class LocalGroupClient(LocalClient[Group]):
    """Local client exposing Project-related operations."""

    def __init__(self, service: GroupService) -> None:
        super().__init__(service, Group)
        self.service: GroupService = service

    def list_tasks(self, id: UUID) -> list[Task]:
        return self.service.list_tasks(id)

    def list_projects(self, id: UUID) -> list[Project]:
        return self.service.list_projects(id)
