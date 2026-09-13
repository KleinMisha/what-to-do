"""Workflows centered around invoking the `projects` command group."""

from typer.testing import CliRunner

from tests.integration.cli.helpers import contains_uuid, parse_id
from what_to_do.cli.entrypoint import app


def test_project_lifecycle(cli_client: CliRunner) -> None:
    """Create, retrieve, and update a project."""

    # Create a group for the project.
    result = cli_client.invoke(app, ["groups", "create", "--name", "CLI test group"])
    assert result.exit_code == 0
    assert contains_uuid(result.stdout)
    assert "CLI test group" in result.stdout
    group_id = parse_id(result.stdout)
    assert group_id is not None

    # Create the project.
    result = cli_client.invoke(
        app, ["projects", "create", "--name", "CLI test", "--group_id", str(group_id)]
    )
    assert result.exit_code == 0
    assert contains_uuid(result.stdout)
    assert "CLI test" in result.stdout
    project_id = parse_id(result.stdout)
    assert project_id is not None

    # Retrieve the project.
    result = cli_client.invoke(app, ["projects", "get", str(project_id)])
    assert result.exit_code == 0
    assert str(project_id) in result.stdout

    # Update the project.
    result = cli_client.invoke(
        app, ["projects", "update", str(project_id), "-n", "Updated CLI test"]
    )
    assert result.exit_code == 0
    assert str(project_id) in result.stdout


def test_list_all_projects(cli_client: CliRunner) -> None:
    """Get all projects."""

    # Create a group for the project.
    result = cli_client.invoke(app, ["groups", "create", "--name", "CLI test group"])
    assert result.exit_code == 0
    group_id = parse_id(result.stdout)
    assert group_id is not None

    # Create two projects.
    result = cli_client.invoke(
        app,
        ["projects", "create", "--name", "First project", "--group_id", str(group_id)],
    )
    assert result.exit_code == 0
    project_1 = parse_id(result.stdout)
    assert project_1 is not None

    result = cli_client.invoke(
        app,
        ["projects", "create", "--name", "Second project", "--group_id", str(group_id)],
    )
    assert result.exit_code == 0
    project_2 = parse_id(result.stdout)
    assert project_2 is not None

    # list all projects.
    result = cli_client.invoke(app, ["projects", "list"])
    assert result.exit_code == 0
    assert str(project_1) in result.stdout
    assert str(project_2) in result.stdout


def test_project_move_moves_its_tasks(cli_client: CliRunner) -> None:
    """Moving a project to another group also moves its tasks."""

    # Create two groups.
    result = cli_client.invoke(app, ["groups", "create", "--name", "Group A"])
    assert result.exit_code == 0
    group_a = parse_id(result.stdout)
    assert group_a is not None

    result = cli_client.invoke(app, ["groups", "create", "--name", "Group B"])
    assert result.exit_code == 0
    group_b = parse_id(result.stdout)
    assert group_b is not None

    # Create a project in group A.
    result = cli_client.invoke(
        app,
        ["projects", "create", "--name", "Project", "--group_id", str(group_a)],
    )
    assert result.exit_code == 0
    project_id = parse_id(result.stdout)
    assert project_id is not None

    # Create a task assigned to the project.
    result = cli_client.invoke(
        app,
        [
            "tasks",
            "create",
            "--title",
            "Task",
            "--gid",
            str(group_a),
            "--pid",
            str(project_id),
        ],
    )
    assert result.exit_code == 0
    task_id = parse_id(result.stdout)
    assert task_id is not None

    # Move the project to group B.
    result = cli_client.invoke(
        app, ["projects", "assign", str(project_id), "--group", str(group_b)]
    )
    assert result.exit_code == 0

    # Verify that the task was moved with the project.
    ## Task and project no longer associated to group A
    result = cli_client.invoke(app, ["groups", "projects", str(group_a)])
    assert result.exit_code == 0
    assert str(project_id) not in result.stdout

    result = cli_client.invoke(app, ["groups", "tasks", str(group_a)])
    assert result.exit_code == 0
    assert str(task_id) not in result.stdout

    ## Task and project now associated to group B
    result = cli_client.invoke(app, ["groups", "projects", str(group_b)])
    assert result.exit_code == 0
    assert str(project_id) in result.stdout
    result = cli_client.invoke(app, ["groups", "tasks", str(group_b)])
    assert result.exit_code == 0
    assert str(task_id) in result.stdout


def test_delete_project_removes_tasks_by_default(cli_client: CliRunner) -> None:
    """Deleting a project deletes its tasks by default."""

    # Create a group.
    result = cli_client.invoke(app, ["groups", "create", "--name", "CLI test group"])
    assert result.exit_code == 0
    group_id = parse_id(result.stdout)
    assert group_id is not None

    # Create a project.
    result = cli_client.invoke(
        app, ["projects", "create", "--name", "CLI test", "--group_id", str(group_id)]
    )
    assert result.exit_code == 0
    project_id = parse_id(result.stdout)
    assert project_id is not None

    # Create a task assigned to the project.
    result = cli_client.invoke(
        app,
        [
            "tasks",
            "create",
            "--title",
            "Task",
            "--gid",
            str(group_id),
            "--pid",
            str(project_id),
        ],
    )
    assert result.exit_code == 0
    task_id = parse_id(result.stdout)
    assert task_id is not None

    # Delete the project.
    result = cli_client.invoke(app, ["projects", "delete", str(project_id)])
    assert result.exit_code == 0

    # Verify that both project and task were deleted.
    assert cli_client.invoke(app, ["projects", "get", str(project_id)]).exit_code == 1
    assert cli_client.invoke(app, ["tasks", "get", str(task_id)]).exit_code == 1


def test_delete_project_can_keep_tasks(cli_client: CliRunner) -> None:
    """Deleting a project can preserve its tasks without their assignment."""

    # Create a group.
    result = cli_client.invoke(app, ["groups", "create", "--name", "CLI test group"])
    assert result.exit_code == 0
    group_id = parse_id(result.stdout)
    assert group_id is not None

    # Create a project.
    result = cli_client.invoke(
        app, ["projects", "create", "--name", "CLI test", "--group_id", str(group_id)]
    )
    assert result.exit_code == 0
    project_id = parse_id(result.stdout)
    assert project_id is not None

    # Create a task assigned to the project.
    result = cli_client.invoke(
        app,
        [
            "tasks",
            "create",
            "--title",
            "Task",
            "--gid",
            str(group_id),
            "--pid",
            str(project_id),
        ],
    )
    assert result.exit_code == 0
    task_id = parse_id(result.stdout)
    assert task_id is not None

    # Delete the project, but preserve the task.
    result = cli_client.invoke(
        app, ["projects", "delete", str(project_id), "--keep-tasks"]
    )
    assert result.exit_code == 0

    # Verify that project no longer exists
    assert cli_client.invoke(app, ["projects", "get", str(project_id)]).exit_code == 1

    # Verify that task still exists
    assert cli_client.invoke(app, ["tasks", "get", str(task_id)]).exit_code == 0


def test_list_project_tasks(cli_client: CliRunner) -> None:
    """Get all tasks assigned to a project."""

    # Create a group.
    result = cli_client.invoke(app, ["groups", "create", "--name", "CLI test group"])
    assert result.exit_code == 0
    group_id = parse_id(result.stdout)
    assert group_id is not None

    # Create a project.
    result = cli_client.invoke(
        app, ["projects", "create", "--name", "CLI test", "--group_id", str(group_id)]
    )
    assert result.exit_code == 0
    project_id = parse_id(result.stdout)
    assert project_id is not None

    # Create two tasks assigned to the project.
    result = cli_client.invoke(
        app,
        [
            "tasks",
            "create",
            "--title",
            "First Task",
            "--gid",
            str(group_id),
            "--pid",
            str(project_id),
        ],
    )
    assert result.exit_code == 0
    task_1 = parse_id(result.stdout)
    assert task_1 is not None

    result = cli_client.invoke(
        app,
        [
            "tasks",
            "create",
            "--title",
            "Second Task",
            "--gid",
            str(group_id),
            "--pid",
            str(project_id),
        ],
    )
    assert result.exit_code == 0
    task_2 = parse_id(result.stdout)
    assert task_2 is not None

    # Get all tasks assigned to the project.
    result = cli_client.invoke(app, ["projects", "tasks", str(project_id)])

    # Assert that both tasks are returned.
    assert str(task_1) in result.stdout
    assert str(task_2) in result.stdout
