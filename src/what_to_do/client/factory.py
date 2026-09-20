"""Creation of Clients"""

from collections.abc import Callable, Generator
from contextlib import contextmanager
from enum import StrEnum
from typing import Any

from sqlalchemy.orm import Session

from what_to_do.client.client import Client
from what_to_do.client.group_clients import LocalGroupClient
from what_to_do.client.local_client import CRUDService, LocalClient
from what_to_do.client.project_clients import LocalProjectClient
from what_to_do.client.task_clients import LocalTaskClient
from what_to_do.db.database import db_session
from what_to_do.service.factory import (
    create_group_service,
    create_project_service,
    create_task_service,
)
from what_to_do.tasks.models import ResourceType

type RemoteClient[T] = LocalClient[T]  # Todo: replace with actual remote client later
type ServiceFactory = Callable[[Session], CRUDService[Any]]
type LocalClientFactory = Callable[[Any], LocalClient[Any]]
type RemoteClientFactory = Callable[[Any], RemoteClient[Any]]
type ClientGenerator = Callable[[ResourceType], Client[Any]]


# Client selection
class ClientMode(StrEnum):
    LOCAL = "local"
    REMOTE = "remote"


# Local Client construction
SERVICE_FACTORIES: dict[ResourceType, ServiceFactory] = {
    ResourceType.TASKS: create_task_service,
    ResourceType.PROJECTS: create_project_service,
    ResourceType.GROUPS: create_group_service,
}

LOCAL_CLIENT_FACTORIES: dict[ResourceType, LocalClientFactory] = {
    ResourceType.TASKS: LocalTaskClient,
    ResourceType.PROJECTS: LocalProjectClient,
    ResourceType.GROUPS: LocalGroupClient,
}


@contextmanager
def get_local_client(
    resource: ResourceType,
    db_url: str,
) -> Generator[LocalClient[Any]]:
    """Setup a local client for resource"""

    service_factory = SERVICE_FACTORIES[resource]
    client_factory = LOCAL_CLIENT_FACTORIES[resource]
    with db_session(db_url) as db:
        service = service_factory(db)
        yield client_factory(service)


@contextmanager
def get_client(
    client_mode: ClientMode,
    resource: ResourceType,
    db_url: str,
) -> Generator[Client[Any]]:
    """Generate / configure Client"""
    if client_mode == ClientMode.LOCAL:
        context = get_local_client(resource, db_url)
    else:
        context = get_local_client(
            resource, db_url
        )  # Todo: replace with actual remote client later

    with context as client:
        yield client
