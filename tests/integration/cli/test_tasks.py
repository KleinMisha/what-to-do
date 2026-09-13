"""Workflows centered around invoking the `tasks` command group."""

from typer.testing import CliRunner

from tests.integration.cli.helpers import contains_uuid, parse_id
from what_to_do.cli.entrypoint import app


def test_task_lifecycle(cli_client: CliRunner) -> None:
    """Create, retrieve, update, delete a task."""

    # Create a group for the task.
    result = cli_client.invoke(app, ["groups", "create", "--name", "A group"])
    group_id = parse_id(result.stdout)

    # Create the task.
    result = cli_client.invoke(
        app, ["tasks", "create", "--title", "CLI test", "--group_id", str(group_id)]
    )
    task_id = parse_id(result.stdout)
    assert task_id is not None
    assert result.exit_code == 0
    assert contains_uuid(result.stdout)
    assert str(task_id) in result.stdout
    assert "CLI test" in result.stdout

    # Retrieve the task.
    result = cli_client.invoke(app, ["tasks", "get", str(task_id)])
    assert result.exit_code == 0
    assert contains_uuid(result.stdout)
    assert str(task_id) in result.stdout

    # Update the task.
    result = cli_client.invoke(
        app,
        [
            "tasks",
            "update",
            str(task_id),
            "--description",
            "Updated description",
            "--title",
            "Updated",
        ],
    )
    assert result.exit_code == 0
    assert str(task_id) in result.stdout
    assert "Updated" in result.stdout

    # Delete the task
    result = cli_client.invoke(app, ["tasks", "delete", str(task_id)])
    assert result.exit_code == 0
    assert str(task_id) in result.stdout

    # get should fail
    result = cli_client.invoke(app, ["tasks", "get", str(task_id)])
    assert result.exit_code == 1


def test_list_all_tasks(cli_client: CliRunner) -> None:
    """Get all tasks."""

    # Create a group for the task.
    result = cli_client.invoke(app, ["groups", "create", "--name", "A group"])
    group_id = parse_id(result.stdout)

    # Create two tasks.
    result = cli_client.invoke(
        app, ["tasks", "create", "--title", "First", "--group_id", str(group_id)]
    )
    first_task = parse_id(result.stdout)

    result = cli_client.invoke(
        app, ["tasks", "create", "--title", "Second", "--group_id", str(group_id)]
    )
    second_task = parse_id(result.stdout)

    # list all tasks
    result = cli_client.invoke(app, ["tasks", "list"])

    # Assert that both tasks are returned.
    assert result.exit_code == 0
    assert str(first_task) in result.stdout
    assert str(second_task) in result.stdout


def test_task_can_move_between_groups(cli_client: CliRunner) -> None:
    """Move a task from one group to another."""

    # Create two groups.
    result = cli_client.invoke(app, ["groups", "create", "--name", "Group A"])
    assert result.exit_code == 0
    group_a = parse_id(result.stdout)
    assert group_a is not None

    result = cli_client.invoke(app, ["groups", "create", "--name", "Group B"])
    assert result.exit_code == 0
    group_b = parse_id(result.stdout)
    assert group_b is not None

    # Create a task in group A.
    result = cli_client.invoke(
        app, ["tasks", "create", "--title", "CLI test", "--gid", str(group_a)]
    )
    assert result.exit_code == 0
    task_id = parse_id(result.stdout)
    assert task_id is not None

    # Move the task to group B.
    result = cli_client.invoke(
        app, ["tasks", "assign", str(task_id), "-g", str(group_b)]
    )
    assert result.exit_code == 0

    # Verify task has moved to group B
    ## Task is no longer associated to group A
    result = cli_client.invoke(app, ["groups", "tasks", str(group_a)])
    assert result.exit_code == 0
    assert str(task_id) not in result.stdout

    ## Task is now associated to group B
    result = cli_client.invoke(app, ["groups", "tasks", str(group_b)])
    assert result.exit_code == 0
    assert str(task_id) in result.stdout


def test_task_can_be_assigned_and_unassigned_from_project(
    cli_client: CliRunner,
) -> None:
    """Assign a task to a project and subsequently remove the assignment."""

    # Create a group.
    result = cli_client.invoke(app, ["groups", "create", "--name", "A group"])
    group_id = parse_id(result.stdout)

    # Create a project.
    result = cli_client.invoke(
        app, ["projects", "create", "--name", "A project", "--group_id", str(group_id)]
    )
    project_id = parse_id(result.stdout)
    assert result.exit_code == 0
    assert project_id is not None

    # Create an unassigned task.
    result = cli_client.invoke(
        app,
        ["tasks", "create", "--title", "CLI test", "--gid", str(group_id)],
    )
    task_id = parse_id(result.stdout)

    # Assign the task to the project.
    result = cli_client.invoke(
        app, ["tasks", "assign", str(task_id), "-p", str(project_id)]
    )
    assert result.exit_code == 0

    # Verify task is associated to project
    result = cli_client.invoke(app, ["projects", "tasks", str(project_id)])
    assert result.exit_code == 0
    assert str(task_id) in result.stdout

    # Remove the project assignment.
    result = cli_client.invoke(app, ["tasks", "assign", str(task_id), "--no-project"])
    assert result.exit_code == 0

    # Verify task is no longer associated to project
    result = cli_client.invoke(app, ["projects", "tasks", str(project_id)])
    assert result.exit_code == 0
    assert str(task_id) not in result.stdout


def test_list_empty(cli_client: CliRunner) -> None:
    """when no resources to list, simply display a message."""
    result = cli_client.invoke(app, ["tasks", "list"])
    assert result.exit_code == 0
    assert result.stdout != ""
