"""Helpers used by multiple command groups."""

from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import fields
from typing import Any

from rich.table import Table

from what_to_do.cli.settings import get_cli_settings
from what_to_do.cli.themes import get_console
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


type Resource = Group | Project | Task


def render_resource_table(items: list[Resource]) -> None:
    """Display table with given resources"""

    # create table
    resource_type = type(items[0])
    table = Table(title=f"{resource_type.__name__}", header_style="heading")
    for field in fields(resource_type):
        table.add_column(field.name)

    for item in items:
        row_entry = [str(getattr(item, field.name)) for field in fields(resource_type)]
        table.add_row(*row_entry)

    # display to console
    console = get_console()
    console.print(table)


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
