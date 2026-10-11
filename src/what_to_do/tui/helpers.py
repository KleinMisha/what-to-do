from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from what_to_do.client.client import Client
from what_to_do.client.factory import get_client
from what_to_do.tasks.models import ResourceType
from what_to_do.tui.settings import get_tui_settings


@contextmanager
def get_tui_client(
    resource: ResourceType,
) -> Generator[Client[Any]]:
    """Configure the CLI client with CLI-specific settings."""
    settings = get_tui_settings()

    # ensure the database file exists
    if not settings.database_path.exists():
        settings.database_path.parent.mkdir(parents=True, exist_ok=True)
        settings.database_path.touch(exist_ok=True)

    with get_client(
        client_mode=settings.client_mode,
        db_url=settings.database_url,
        resource=resource,
    ) as client:
        yield client
