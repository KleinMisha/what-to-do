"""Creation of Clients"""

from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import Any

from sqlalchemy.orm import Session

from what_to_do.client.local_client import CRUDService, LocalClient
from what_to_do.client.project_clients import LocalProjectClient
from what_to_do.client.task_clients import LocalTaskClient
from what_to_do.db.database import db_session
from what_to_do.service.factory import (
    create_group_service,
    create_project_service,
    create_task_service,
)
from what_to_do.tasks.models import Group, ResourceType

type ServiceFactory = Callable[[Session], CRUDService[Any]]
type LocalClientFactory = Callable[[Any], LocalClient[Any]]


# Local Client construction
SERVICE_FACTORIES: dict[ResourceType, ServiceFactory] = {
    ResourceType.TASKS: create_task_service,
    ResourceType.PROJECTS: create_project_service,
    ResourceType.GROUPS: create_group_service,
}

LOCAL_CLIENT_FACTORIES: dict[ResourceType, LocalClientFactory] = {
    ResourceType.TASKS: LocalTaskClient,
    ResourceType.PROJECTS: LocalProjectClient,
    ResourceType.GROUPS: lambda service: LocalClient(service, Group),
}


@contextmanager
def local_client(resource: ResourceType) -> Generator[LocalClient[Any]]:
    """Setup a local client for resource"""

    service_factory = SERVICE_FACTORIES[resource]
    client_factory = LOCAL_CLIENT_FACTORIES[resource]
    with db_session() as db:
        service = service_factory(db)
        yield client_factory(service)
