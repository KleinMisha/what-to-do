"""Command group: `projects`

── project
│   └── assign <id> --group ...
"""

from typing import Annotated
from uuid import UUID, uuid4

from typer import Argument, Exit, Option, Typer, echo

from what_to_do.cli.helpers import TOOL_NAME, render_project, render_task
from what_to_do.client.factory import ResourceType, get_client
from what_to_do.client.project_clients import LocalProjectClient
from what_to_do.core.exceptions import ResourceNotFoundError
from what_to_do.tasks.models import Project, Task

app = Typer(name="projects")


@app.command("list")
def list_projects() -> None:
    """Show all available projects


    #TODO add options for displaying
    #TODO 1. list -a/--all or --long shows complete table including group id (or name), description , and more.
    """

    with get_client(ResourceType.PROJECTS) as client:
        projects: list[Project] = client.get_all()

    if not projects:
        echo(
            f"No projects found. Create a new project with `{TOOL_NAME} projects create <ARGS> [OPTIONS]`"
        )

    for project in projects:
        echo(render_project(project))
    raise Exit(code=0)


@app.command()
def get(id: Annotated[UUID, Argument(help="Project ID.")]) -> None:
    """Get info for a given Project."""
    try:
        with get_client(ResourceType.PROJECTS) as client:
            project = client.get(id)

        echo(render_project(project))
        raise Exit(code=0)

    except ResourceNotFoundError as e:
        echo(f"{type(e).__name__} : {e!s}")
        raise Exit(code=1)


@app.command()
def create(
    name: Annotated[str, Option("--name", "-n", help="Name of the project.")],
    group_id: Annotated[
        UUID,
        Option(
            "--group_id", "--gid", help="ID of the group this project falls under. "
        ),
    ],
    description: Annotated[
        str | None, Option("--description", "-d", help="Detailed description. ")
    ] = None,
) -> None:
    """Create a new project."""
    project_id = uuid4()
    with get_client(ResourceType.PROJECTS) as client:
        new: Project = client.create(
            project_id,
            name=name,
            description=description or "",
            group_id=group_id,
        )

    echo(f"Created new project: \n {render_project(new)}")
    raise Exit(code=0)


@app.command()
def update(
    project_id: Annotated[UUID, Argument(help="Project ID.")],
    name: Annotated[
        str | None, Option("--name", "-n", help="Name of the project.")
    ] = None,
    group_id: Annotated[
        UUID | None,
        Option(
            "--group_id", "--gid", help="ID of the group this project falls under. "
        ),
    ] = None,
    description: Annotated[
        str | None, Option("--description", "-d", help="Detailed description. ")
    ] = None,
) -> None:
    """Create an existing project."""
    try:
        with get_client(ResourceType.PROJECTS) as client:
            original: Project = client.get(project_id)

            updated: Project = client.update(
                project_id,
                name=name or original.name,
                description=description or original.description,
                group_id=group_id or original.group_id,
            )

        echo(f"Updated project: \n {render_project(updated)}")
        raise Exit(code=0)

    except ResourceNotFoundError as e:
        echo(f"{type(e).__name__} : {e!s}")
        raise Exit(code=1)


@app.command()
def delete(
    id: Annotated[UUID, Argument(help="Project ID.")],
    keep_tasks: Annotated[
        bool,
        Option(
            "--keep-tasks",
            help="Keep the tasks assigned to the project and move them directly under the group (no project assignment.)",
        ),
    ] = False,
) -> None:

    try:
        with get_client(ResourceType.PROJECTS) as client:
            assert isinstance(client, LocalProjectClient)
            deleted = client.delete(id, keep_tasks=keep_tasks)

        echo(f"Deleted project: \n {render_project(deleted)}")
        if keep_tasks:
            echo("Kept all tasks assigned to project")

        raise Exit(code=0)

    except ResourceNotFoundError as e:
        echo(f"{type(e).__name__} : {e!s}")
        raise Exit(code=1)


@app.command()
def assign(
    id: Annotated[UUID, Argument(help="Project ID.")],
    group: Annotated[
        UUID,
        Option(
            "--group",
            help="Group ID.",
        ),
    ],
) -> None:
    try:
        with get_client(ResourceType.PROJECTS) as client:
            assert isinstance(client, LocalProjectClient)
            updated: Project = client.assign(project_id=id, group_id=group)

        echo(f"Updated project: \n {render_project(updated)}")
        raise Exit(code=0)

    except ResourceNotFoundError as e:
        echo(f"{type(e).__name__} : {e!s}")
        raise Exit(code=1)


@app.command("tasks")
def list_tasks(id: Annotated[UUID, Argument(help="Project ID.")]) -> None:
    """List all tasks assigned to a project."""

    try:
        with get_client(ResourceType.PROJECTS) as client:
            assert isinstance(client, LocalProjectClient)
            tasks: list[Task] = client.list_tasks(id)

        if not tasks:
            echo(f"No tasks in project {id}")

        for task in tasks:
            echo(render_task(task))

        raise Exit(code=0)

    except ResourceNotFoundError as e:
        echo(f"{type(e).__name__} : {e!s}")
        raise Exit(code=1)
