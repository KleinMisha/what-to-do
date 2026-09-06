"""Clients for Task resource."""

from typing import Protocol
from uuid import UUID

from what_to_do.client.local_client import CRUDService, LocalClient
from what_to_do.tasks.models import Task


class TaskService(CRUDService[Task], Protocol):
    """Methods the client defined below expects to be present."""

    def assign(
        self,
        task: Task,
        *,
        group_id: UUID,
        project_id: UUID | None,
    ) -> Task: ...


class LocalTaskClient(LocalClient[Task]):
    """Local client exposing Task related operations.

    extends LocalClient with Task-specific operations (assignments)
    """

    def __init__(self, service: TaskService) -> None:
        super().__init__(service, Task)
        self.service: TaskService = service

    def assign(self, *, task_id: UUID, project_id: UUID | None, group_id: UUID) -> Task:
        task = self.service.get(task_id)
        return self.service.assign(task, group_id=group_id, project_id=project_id)
