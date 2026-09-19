"""Creation of Clients"""

from collections.abc import Callable, Generator
from contextlib import AbstractContextManager, contextmanager
from enum import StrEnum
from typing import Any

from sqlalchemy.orm import Session

from what_to_do.cli.settings import get_cli_settings
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
type ClientContext = Callable[[ResourceType], AbstractContextManager[Client[Any]]]


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
def get_local_client(resource: ResourceType) -> Generator[LocalClient[Any]]:
    """Setup a local client for resource"""

    service_factory = SERVICE_FACTORIES[resource]
    client_factory = LOCAL_CLIENT_FACTORIES[resource]
    with db_session() as db:
        service = service_factory(db)
        yield client_factory(service)


CLIENT_CONTEXTS: dict[ClientMode, ClientContext] = {ClientMode.LOCAL: get_local_client}


@contextmanager
def get_client(resource: ResourceType) -> Generator[Client[Any]]:
    """Generate / configure Client"""
    settings = get_cli_settings()
    context = CLIENT_CONTEXTS[settings.client_mode]
    with context(resource) as client:
        yield client
