from typing import Any

from fastapi.testclient import TestClient


def test_task_lifecycle(client: TestClient) -> None:
    """Create, retrieve, update, delete a task."""

    # Create a group for the task.
    group_response = client.post(
        "/api/v1/groups",
        json={"name": "Personal"},
    )
    assert group_response.status_code == 201
    group: dict[str, Any] = group_response.json()

    # Create the task.
    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Build homepage",
            "description": "Create the initial homepage",
            "group_id": group["id"],
            "project_id": None,
        },
    )
    assert response.status_code == 201
    task: dict[str, Any] = response.json()
    task_id = task["id"]

    # Retrieve the task.
    response = client.get(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json() == task

    # Update the task.
    response = client.put(
        f"/api/v1/tasks/{task_id}",
        json={
            "title": "Build new homepage",
            "description": "Updated description",
            "group_id": group["id"],
            "project_id": None,
        },
    )
    assert response.status_code == 200
    updated_task: dict[str, Any] = response.json()
    assert updated_task["title"] == "Build new homepage"
    assert updated_task["description"] == "Updated description"

    # Delete the task
    response = client.delete(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 200
    deleted_task: dict[str, Any] = response.json()
    assert deleted_task == updated_task

    # get should fail
    assert client.get(f"/api/v1/tasks/{task_id}").status_code == 404


def test_list_all_tasks(client: TestClient) -> None:
    """Get all tasks."""

    # Create a group for the tasks.
    group_response = client.post(
        "/api/v1/groups",
        json={"name": "Personal"},
    )
    assert group_response.status_code == 201
    group: dict[str, Any] = group_response.json()

    # Create two tasks.
    task_1_response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Task 1",
            "description": "First task",
            "group_id": group["id"],
            "project_id": None,
        },
    )
    assert task_1_response.status_code == 201
    task_1: dict[str, Any] = task_1_response.json()

    task_2_response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Task 2",
            "description": "Second task",
            "group_id": group["id"],
            "project_id": None,
        },
    )
    assert task_2_response.status_code == 201
    task_2: dict[str, Any] = task_2_response.json()

    # Perform GET call on /tasks.
    response = client.get("/api/v1/tasks")

    # Assert that both tasks are returned.
    assert response.status_code == 200
    tasks: list[dict[str, Any]] = response.json()
    assert {task["id"] for task in tasks} == {
        task_1["id"],
        task_2["id"],
    }


def test_task_can_move_between_groups(client: TestClient) -> None:
    """Move a task from one group to another."""

    # Create two groups.
    group_a_response = client.post(
        "/api/v1/groups",
        json={"name": "Group A"},
    )
    assert group_a_response.status_code == 201
    group_a: dict[str, Any] = group_a_response.json()

    group_b_response = client.post(
        "/api/v1/groups",
        json={"name": "Group B"},
    )
    assert group_b_response.status_code == 201
    group_b: dict[str, Any] = group_b_response.json()

    # Create a task in group A.
    task_response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Task",
            "description": "Description",
            "group_id": group_a["id"],
            "project_id": None,
        },
    )
    assert task_response.status_code == 201
    task: dict[str, Any] = task_response.json()

    # Move the task to group B.
    response = client.patch(
        f"/api/v1/tasks/{task['id']}/group",
        json={
            "group_id": group_b["id"],
            "project_id": None,
        },
    )
    assert response.status_code == 200
    assert response.json()["group_id"] == group_b["id"]


def test_task_can_be_assigned_and_unassigned_from_project(
    client: TestClient,
) -> None:
    """Assign a task to a project and subsequently remove the assignment."""

    # Create a group.
    group_response = client.post(
        "/api/v1/groups",
        json={"name": "Personal"},
    )
    assert group_response.status_code == 201
    group: dict[str, Any] = group_response.json()

    # Create a project.
    project_response = client.post(
        "/api/v1/projects",
        json={
            "name": "Website",
            "description": "Website project",
            "group_id": group["id"],
        },
    )
    assert project_response.status_code == 201
    project: dict[str, Any] = project_response.json()

    # Create an unassigned task.
    task_response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Homepage",
            "description": "Build it",
            "group_id": group["id"],
            "project_id": None,
        },
    )
    assert task_response.status_code == 201
    task: dict[str, Any] = task_response.json()

    # Assign the task to the project.
    response = client.patch(
        f"/api/v1/tasks/{task['id']}/project",
        json={"project_id": project["id"]},
    )
    assert response.status_code == 200
    assert response.json()["project_id"] == project["id"]

    # Remove the project assignment.
    response = client.patch(
        f"/api/v1/tasks/{task['id']}/project",
        json={"project_id": None},
    )
    assert response.status_code == 200
    assert response.json()["project_id"] is None
