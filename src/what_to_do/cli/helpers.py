"""Helpers used by multiple command groups."""

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from what_to_do.cli.settings import get_cli_settings
from what_to_do.client.factory import Client, get_client
from what_to_do.tasks.models import Group, Project, ResourceType, Task

# todo: adjust once settled on the actual tool name
TOOL_NAME = "what-to-do"


def render_group(group: Group) -> str:
    """Render a string with Task information."""

    # TODO make information more rich. Include options to show more / less
    return f"[{group.id}] \t {group.name}"


def render_task(task: Task) -> str:
    """Render a string with Task information."""

    # TODO make information more rich. Include options to show more / less
    return f"[{task.id}] \t {task.title}"


def render_project(project: Project) -> str:
    """Render a string with Project information."""

    # TODO make information more rich. Include options to show more / less
    return f"[{project.id}] \t {project.name}"


@contextmanager
def get_cli_client(
    resource: ResourceType,
) -> Generator[Client[Any]]:
    """Configure the CLI client with CLI-specific settings."""
    settings = get_cli_settings()

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
