"""Workflows centered around invoking the `groups` command group."""

import re
from uuid import UUID

from typer.testing import CliRunner

from what_to_do.cli.entrypoint import app


def parse_id(entry: str) -> UUID | None:
    """
    Extract a UUID from a string."
    """
    _uuid = re.compile(
        r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
    )
    match = _uuid.search(entry)
    return UUID(match.group(0)) if match else None


def contains_uuid(text: str) -> bool:
    """Determine if a given text indeed contains any UUID"""
    return parse_id(text) is not None


def test_group_lifecycle(cli_client: CliRunner) -> None:
    """Create, retrieve, and update a group."""
    # Create a group.
    result = cli_client.invoke(app, ["groups", "create", "--name", "CLI test"])
    assert result.exit_code == 0
    assert contains_uuid(result.stdout)
    assert "CLI test" in result.stdout

    group_id = parse_id(result.stdout)

    # Retrieve the group.
    result = cli_client.invoke(app, ["groups", "get", str(group_id)])
    assert result.exit_code == 0
    assert str(group_id) in result.stdout

    # Update the group.
    result = cli_client.invoke(
        app, ["groups", "update", str(group_id), "-n", "Updated CLI test"]
    )
    assert result.exit_code == 0
    assert str(group_id) in result.stdout


def test_group_lists_projects_and_tasks(cli_client: CliRunner) -> None:
    """List the projects and tasks belonging to a group."""
    # Create the group.
    result = cli_client.invoke(app, ["groups", "create", "--name", "CLI test"])
    assert result.exit_code == 0
    assert contains_uuid(result.stdout)
    assert "CLI test" in result.stdout

    group_id = parse_id(result.stdout)

    # Create a project in the group.
    result = cli_client.invoke(
        app, ["projects", "create", "--name", "CLI test proj", "--gid", str(group_id)]
    )

    assert result.exit_code == 0
    assert contains_uuid(result.stdout)
    assert "CLI test proj" in result.stdout

    project_id = parse_id(result.stdout)

    # Create a task in the group and project.
    result = cli_client.invoke(
        app, ["tasks", "create", "--title", "Test the CLI", "--gid", str(group_id)]
    )
    assert result.exit_code == 0
    assert contains_uuid(result.stdout)
    assert "Test the CLI" in result.stdout

    task_id = parse_id(result.stdout)

    # Verify that the group exposes its project.
    result = cli_client.invoke(app, ["groups", "projects", str(group_id)])
    assert result.exit_code == 0
    assert contains_uuid(result.stdout)
    assert str(project_id) in result.stdout

    # Verify that the group exposes its task.
    result = cli_client.invoke(app, ["groups", "tasks", str(group_id)])
    assert result.exit_code == 0
    assert contains_uuid(result.stdout)
    assert str(task_id) in result.stdout


def test_delete_group_cascades_projects_and_tasks(cli_client: CliRunner) -> None:
    """Deleting a group also deletes its projects and tasks."""
    # Build a group hierarchy: group -> project -> task.
    result = cli_client.invoke(app, ["groups", "create", "--name", "CLI test"])
    group_id = parse_id(result.stdout)

    result = cli_client.invoke(
        app, ["projects", "create", "--name", "CLI test proj", "--gid", str(group_id)]
    )
    project_id = parse_id(result.stdout)

    result = cli_client.invoke(
        app, ["tasks", "create", "--title", "Test the CLI", "--gid", str(group_id)]
    )
    task_id = parse_id(result.stdout)

    # Delete the group.
    result = cli_client.invoke(app, ["groups", "delete", str(group_id)])

    # The entire hierarchy should now be gone.
    assert cli_client.invoke(app, ["groups", "get", str(group_id)]).exit_code == 1
    assert cli_client.invoke(app, ["projects", "get", str(project_id)]).exit_code == 1
    assert cli_client.invoke(app, ["tasks", "get", str(task_id)]).exit_code == 1
