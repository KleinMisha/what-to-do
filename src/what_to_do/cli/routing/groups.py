"""Command group: `groups`"""

from typing import Annotated
from uuid import UUID, uuid4

from typer import Argument, Exit, Option, Typer, echo

from what_to_do.cli.helpers import TOOL_NAME, render_group, render_project, render_task
from what_to_do.client.factory import ResourceType, local_client
from what_to_do.client.group_clients import LocalGroupClient
from what_to_do.core.exceptions import ResourceNotFoundError
from what_to_do.tasks.models import Group, Project, Task

app = Typer(name="groups")


@app.command("list")
def list_groups() -> None:
    """Display all available groups."""

    with local_client(ResourceType.GROUPS) as client:
        groups: list[Group] = client.get_all()

    if not groups:
        echo(
            f"No available groups. Create a new group using `{TOOL_NAME} groups create <ARGS> [OPTIONS]`"
        )

    for group in groups:
        echo(render_group(group))

    raise Exit(code=0)


@app.command()
def get(id: Annotated[UUID, Argument(help="Group ID.")]) -> None:
    """Get info for a given Group."""
    try:
        with local_client(ResourceType.GROUPS) as client:
            group = client.get(id)

        echo(render_group(group))
        raise Exit(code=0)

    except ResourceNotFoundError as e:
        echo(f"{type(e).__name__} : {e!s}")
        raise Exit(code=1)


@app.command()
def create(
    name: Annotated[str, Option("--name", "-n", help="Name of the group.")],
) -> None:
    """Create a new group."""
    group_id = uuid4()
    with local_client(ResourceType.GROUPS) as client:
        new: Group = client.create(group_id, name=name)

        echo(f"Created new group: \n {render_group(new)}")
        raise Exit(code=0)


@app.command()
def update(
    id: Annotated[UUID, Argument(help="Group ID.")],
    name: Annotated[
        str | None, Option("--name", "-n", help="Name of the group.")
    ] = None,
) -> None:
    """Update an existing group's info."""

    try:
        with local_client(ResourceType.GROUPS) as client:
            original: Group = client.get(id)
            updated: Group = client.update(
                id,
                name=name or original.name,
            )

            echo(f"Updated group: \n {render_group(updated)}")
            raise Exit(code=0)

    except ResourceNotFoundError as e:
        echo(f"{type(e).__name__} : {e!s}")
        raise Exit(code=1)


@app.command()
def delete(id: Annotated[UUID, Argument(help="Group ID.")]) -> None:
    """Delete a group."""
    try:
        with local_client(ResourceType.GROUPS) as client:
            deleted: Group = client.delete(id)

        echo(f"Deleted group: \n {render_group(deleted)}")
        raise Exit(code=0)

    except ResourceNotFoundError as e:
        echo(f"{type(e).__name__} : {e!s}")
        raise Exit(code=1)


@app.command("tasks")
def list_tasks(id: Annotated[UUID, Argument(help="Group ID.")]) -> None:
    """List all tasks assigned to a group."""

    try:
        with local_client(ResourceType.GROUPS) as client:
            assert isinstance(client, LocalGroupClient)
            tasks: list[Task] = client.list_tasks(id)

        if not tasks:
            echo(f"No tasks in group {id}")

        for task in tasks:
            echo(render_task(task))

        raise Exit(code=0)

    except ResourceNotFoundError as e:
        echo(f"{type(e).__name__} : {e!s}")
        raise Exit(code=1)


@app.command("projects")
def list_projects(id: Annotated[UUID, Argument(help="Group ID.")]) -> None:
    """List all projects assigned to a group."""

    try:
        with local_client(ResourceType.GROUPS) as client:
            assert isinstance(client, LocalGroupClient)
            projects: list[Project] = client.list_projects(id)

        if not projects:
            echo(f"No projects in group {id}")

        for project in projects:
            echo(render_project(project))

        raise Exit(code=0)

    except ResourceNotFoundError as e:
        echo(f"{type(e).__name__} : {e!s}")
        raise Exit(code=1)
