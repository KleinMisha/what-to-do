"""Command group: `tasks`"""

from typing import Annotated
from uuid import UUID, uuid4

from typer import Argument, Exit, Option, Typer, echo

from what_to_do.cli.helpers import TOOL_NAME, render_task
from what_to_do.client.factory import ResourceType, local_client
from what_to_do.client.task_clients import LocalTaskClient
from what_to_do.core.exceptions import InvalidAssignmentError, ResourceNotFoundError
from what_to_do.tasks.models import Priority, Task

app = Typer(name="tasks")


@app.command("list")
def list_tasks() -> None:
    """Show all available tasks


    #TODO add options for displaying tasks
    #TODO 1. list -a/--all or --long shows complete table including group id (or name), description , and more.
    NOTE: For now just only show the task' title. Can format later
    """

    with local_client(ResourceType.TASKS) as client:
        tasks: list[Task] = client.get_all()

    if not tasks:
        echo(
            f"No tasks found. Create a new task with `{TOOL_NAME} tasks create <ARGS> [OPTIONS]`"
        )

    for task in tasks:
        echo(render_task(task))
    raise Exit(code=0)


@app.command()
def get(id: Annotated[UUID, Argument(help="Task ID.")]) -> None:
    """Get info for a given task."""
    try:
        with local_client(ResourceType.TASKS) as client:
            task = client.get(id)

        echo(render_task(task))
        raise Exit(code=0)

    except ResourceNotFoundError as e:
        echo(f"{type(e).__name__} : {e!s}")
        raise Exit(code=1)


@app.command()
def create(
    title: Annotated[str, Option("--title", "-t", help="Name of the task.")],
    group_id: Annotated[
        UUID,
        Option("--group_id", "--gid", help="ID of the group this task falls under. "),
    ],
    description: Annotated[
        str | None, Option("--description", "-d", help="Detailed description. ")
    ] = None,
    project_id: Annotated[
        UUID | None,
        Option(
            "--project_id", "--pid", help="ID of the project this task falls under. "
        ),
    ] = None,
    priority: Annotated[
        Priority, Option("--priority", "-p", help="Priority level")
    ] = Priority.LOW,
) -> None:
    """
    Create a new Task.
    """
    try:
        task_id = uuid4()
        with local_client(ResourceType.TASKS) as client:
            new: Task = client.create(
                task_id,
                title=title,
                description=description or "",
                group_id=group_id,
                project_id=project_id,
                priority=priority,
            )

        echo(f"Created new task: \n {render_task(new)}")
        raise Exit(code=0)
    except (InvalidAssignmentError, ResourceNotFoundError) as e:
        echo(f"{type(e).__name__} : {e!s}")
        raise Exit(code=1)


@app.command()
def update(
    task_id: Annotated[UUID, Argument(help="Task ID.")],
    title: Annotated[str, Option("--title", "-t", help="Task's name")],
    description: Annotated[
        str, Option("--description", "-d", help="Detailed description. ")
    ],
    group_id: Annotated[
        UUID,
        Option("--group_id", "--gid", help="ID of the group this task falls under. "),
    ],
    project_id: Annotated[
        UUID,
        Option(
            "--project_id", "--pid", help="ID of the project this task falls under. "
        ),
    ],
    priority: Annotated[
        Priority, Option("--priority", "-p", help="Priority level")
    ] = Priority.LOW,
) -> None:
    """Update an existing task's info."""
    try:
        with local_client(ResourceType.TASKS) as client:
            updated: Task = client.update(
                task_id,
                title=title,
                description=description,
                group_id=group_id,
                project_id=project_id,
                priority=priority,
            )

        echo(f"Updated task: \n {render_task(updated)}")
        raise Exit(code=0)

    except (InvalidAssignmentError, ResourceNotFoundError) as e:
        echo(f"{type(e).__name__} : {e!s}")
        raise Exit(code=1)


@app.command()
def delete(id: Annotated[UUID, Argument(help="Task ID.")]) -> None:
    """Delete a task"""
    try:
        with local_client(ResourceType.TASKS) as client:
            deleted = client.delete(id)

        echo(f"Deleted task: \n {render_task(deleted)}")
        raise Exit(code=0)

    except ResourceNotFoundError as e:
        echo(f"{type(e).__name__} : {e!s}")
        raise Exit(code=1)


@app.command()
def assign(
    id: Annotated[UUID, Argument(help="Task ID.")],
    group: Annotated[
        UUID,
        Option(
            "--group",
            help="Group ID.",
        ),
    ],
    project: Annotated[
        UUID | None,
        Option(
            "--project",
            help="Project ID. If not entered, the task will be unassigned from it's current project. ",
        ),
    ],
) -> None:
    """Move a project to a different project / group

    Also use this to unassign a task from a project and stay within the same group.
    """
    try:
        with local_client(ResourceType.TASKS) as client:
            assert isinstance(client, LocalTaskClient)
            updated = client.assign(task_id=id, project_id=project, group_id=group)

        echo(f"Updated task: \n {render_task(updated)}")
        raise Exit(code=0)

    except InvalidAssignmentError as e:
        echo(f"{type(e).__name__} : {e!s}")
        raise Exit(code=1)
