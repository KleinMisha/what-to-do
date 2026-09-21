from uuid import uuid4

import pytest
from typer.testing import CliRunner

from tests.integration.cli.helpers import parse_id
from what_to_do.cli.entrypoint import app

# from what_to_do.core.exceptions import InvalidAssignmentError, ResourceNotFoundError

UNKNOWN_ID = uuid4()


@pytest.mark.parametrize(
    "command",
    [
        ("tasks", "get", str(UNKNOWN_ID)),
        ("tasks", "update", str(UNKNOWN_ID)),
        ("tasks", "delete", str(UNKNOWN_ID)),
        (
            "tasks",
            "assign",
            str(UNKNOWN_ID),
            "--group",
            str(UNKNOWN_ID),
            "--project",
            str(UNKNOWN_ID),
        ),
        ("projects", "get", str(UNKNOWN_ID)),
        ("projects", "update", str(UNKNOWN_ID)),
        ("projects", "delete", str(UNKNOWN_ID)),
        ("projects", "assign", str(UNKNOWN_ID), "--group", str(UNKNOWN_ID)),
        ("projects", "tasks", str(UNKNOWN_ID)),
        ("groups", "get", str(UNKNOWN_ID)),
        ("groups", "update", str(UNKNOWN_ID)),
        ("groups", "delete", str(UNKNOWN_ID)),
        ("groups", "tasks", str(UNKNOWN_ID)),
        ("groups", "projects", str(UNKNOWN_ID)),
    ],
)
def test_missing_resource(command: tuple[str, ...], cli_client: CliRunner) -> None:
    """Make sure ResourceNotFoundError is re-raised with a Exit(code=1)"""
    result = cli_client.invoke(app, command)
    print(result.stderr)
    print(result.stdout)
    assert result.exit_code == 1
    assert "ResourceNotFoundError" in result.stdout


def test_task_cannot_use_project_from_different_group(cli_client: CliRunner) -> None:
    """Raise exit code 1 when a task and project belong to different groups."""

    # Create two groups.
    result = cli_client.invoke(app, ["groups", "create", "--name", "First"])
    first_group = parse_id(result.stdout)

    result = cli_client.invoke(app, ["groups", "create", "--name", "Second"])
    second_group = parse_id(result.stdout)

    # Create a project in group B.
    result = cli_client.invoke(
        app,
        [
            "projects",
            "create",
            "--name",
            "In the second group",
            "--group_id",
            str(second_group),
        ],
    )
    project_id = parse_id(result.stdout)
    assert project_id is not None

    # Attempt to create a task in group A using the project from group B.
    result = cli_client.invoke(
        app,
        [
            "tasks",
            "create",
            "--title",
            "invalid task",
            "--group_id",
            str(first_group),
            "--project_id",
            str(project_id),
        ],
    )
    print(result.stdout)
    print(result.stderr)
    assert result.exit_code == 1
    assert "InvalidAssignmentError" in result.stdout
