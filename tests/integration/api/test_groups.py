from typing import Any

from fastapi.testclient import TestClient


def test_group_lifecycle(client: TestClient) -> None:
    """Create, retrieve, and update a group."""
    # Create a group.
    response = client.post(
        "/api/v1/groups",
        json={"name": "Personal"},
    )

    assert response.status_code == 201
    group: dict[str, Any] = response.json()
    group_id = group["id"]

    assert group["name"] == "Personal"

    # Retrieve the group.
    response = client.get(f"/api/v1/groups/{group_id}")

    assert response.status_code == 200
    assert response.json() == group

    # Update the group.
    response = client.put(
        f"/api/v1/groups/{group_id}",
        json={"name": "Work"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Work"


def test_group_lists_projects_and_tasks(client: TestClient) -> None:
    """List the projects and tasks belonging to a group."""
    # Create the group.
    group_response = client.post(
        "/api/v1/groups",
        json={"name": "Personal"},
    )
    assert group_response.status_code == 201
    group: dict[str, Any] = group_response.json()

    # Create a project in the group.
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

    # Create a task in the group and project.
    task_response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Build homepage",
            "description": "Create homepage",
            "group_id": group["id"],
            "project_id": project["id"],
        },
    )
    assert task_response.status_code == 201
    task: dict[str, Any] = task_response.json()

    # Verify that the group exposes its project.
    response = client.get(f"/api/v1/groups/{group['id']}/projects")

    assert response.status_code == 200
    assert {item["id"] for item in response.json()} == {project["id"]}

    # Verify that the group exposes its task.
    response = client.get(f"/api/v1/groups/{group['id']}/tasks")

    assert response.status_code == 200
    assert {item["id"] for item in response.json()} == {task["id"]}


def test_delete_group_cascades_projects_and_tasks(client: TestClient) -> None:
    """Deleting a group also deletes its projects and tasks."""
    # Build a group hierarchy: group -> project -> task.
    group_response = client.post(
        "/api/v1/groups",
        json={"name": "Personal"},
    )
    assert group_response.status_code == 201
    group: dict[str, Any] = group_response.json()

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

    task_response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Homepage",
            "description": "Build it",
            "group_id": group["id"],
            "project_id": project["id"],
        },
    )
    assert task_response.status_code == 201
    task: dict[str, Any] = task_response.json()

    # Delete the group.
    response = client.delete(f"/api/v1/groups/{group['id']}")

    assert response.status_code == 200

    # The entire hierarchy should now be gone.
    assert client.get(f"/api/v1/groups/{group['id']}").status_code == 404
    assert client.get(f"/api/v1/projects/{project['id']}").status_code == 404
    assert client.get(f"/api/v1/tasks/{task['id']}").status_code == 404


def test_list_all_groups(client: TestClient) -> None:
    """Get all groups."""

    # Create two groups.
    group_1_response = client.post(
        "/api/v1/groups",
        json={"name": "Personal"},
    )
    assert group_1_response.status_code == 201
    group_1: dict[str, Any] = group_1_response.json()

    group_2_response = client.post(
        "/api/v1/groups",
        json={"name": "Work"},
    )
    assert group_2_response.status_code == 201
    group_2: dict[str, Any] = group_2_response.json()

    # Perform GET call on /groups.
    response = client.get("/api/v1/groups")

    # Assert that both groups are returned.
    assert response.status_code == 200
    groups: list[dict[str, Any]] = response.json()
    assert {group["id"] for group in groups} == {
        group_1["id"],
        group_2["id"],
    }
