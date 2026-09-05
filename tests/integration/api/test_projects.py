from typing import Any

from fastapi.testclient import TestClient


def test_project_lifecycle(client: TestClient, api_prefix: str) -> None:
    """Create, retrieve, and update a project."""

    # Create a group for the project.
    group_response = client.post(
        f"{api_prefix}/groups",
        json={"name": "Personal"},
    )
    assert group_response.status_code == 201
    group: dict[str, Any] = group_response.json()

    # Create the project.
    response = client.post(
        f"{api_prefix}/projects",
        json={
            "name": "Website",
            "description": "Personal website",
            "group_id": group["id"],
        },
    )
    assert response.status_code == 201
    project: dict[str, Any] = response.json()
    project_id = project["id"]

    # Retrieve the project.
    response = client.get(f"{api_prefix}/projects/{project_id}")
    assert response.status_code == 200
    assert response.json() == project

    # Update the project.
    response = client.put(
        f"{api_prefix}/projects/{project_id}",
        json={
            "name": "New Website",
            "description": "Updated website",
            "group_id": group["id"],
        },
    )
    assert response.status_code == 200
    updated_project: dict[str, Any] = response.json()
    assert updated_project["name"] == "New Website"
    assert updated_project["description"] == "Updated website"


def test_list_all_projects(client: TestClient, api_prefix: str) -> None:
    """Get all projects."""

    # Create a group for the projects.
    group_response = client.post(
        f"{api_prefix}/groups",
        json={"name": "Personal"},
    )
    assert group_response.status_code == 201
    group: dict[str, Any] = group_response.json()

    # Create two projects.
    project_1_response = client.post(
        f"{api_prefix}/projects",
        json={
            "name": "Website",
            "description": "Personal website",
            "group_id": group["id"],
        },
    )
    assert project_1_response.status_code == 201
    project_1: dict[str, Any] = project_1_response.json()

    project_2_response = client.post(
        f"{api_prefix}/projects",
        json={
            "name": "Garden",
            "description": "Garden project",
            "group_id": group["id"],
        },
    )
    assert project_2_response.status_code == 201
    project_2: dict[str, Any] = project_2_response.json()

    # Perform GET call on /projects.
    response = client.get(f"{api_prefix}/projects")

    # Assert that both projects are returned.
    assert response.status_code == 200
    projects: list[dict[str, Any]] = response.json()
    assert {project["id"] for project in projects} == {
        project_1["id"],
        project_2["id"],
    }


def test_project_move_moves_its_tasks(client: TestClient, api_prefix: str) -> None:
    """Moving a project to another group also moves its tasks."""

    # Create two groups.
    group_a_response = client.post(
        f"{api_prefix}/groups",
        json={"name": "Group A"},
    )
    assert group_a_response.status_code == 201
    group_a: dict[str, Any] = group_a_response.json()

    group_b_response = client.post(
        f"{api_prefix}/groups",
        json={"name": "Group B"},
    )
    assert group_b_response.status_code == 201
    group_b: dict[str, Any] = group_b_response.json()

    # Create a project in group A.
    project_response = client.post(
        f"{api_prefix}/projects",
        json={
            "name": "Website",
            "description": "Website project",
            "group_id": group_a["id"],
        },
    )
    assert project_response.status_code == 201
    project: dict[str, Any] = project_response.json()

    # Create a task assigned to the project.
    task_response = client.post(
        f"{api_prefix}/tasks",
        json={
            "title": "Homepage",
            "description": "Build it",
            "group_id": group_a["id"],
            "project_id": project["id"],
        },
    )
    assert task_response.status_code == 201
    task: dict[str, Any] = task_response.json()

    # Move the project to group B.
    response = client.patch(
        f"{api_prefix}/projects/{project['id']}/group",
        json={"group_id": group_b["id"]},
    )
    assert response.status_code == 200
    assert response.json()["group_id"] == group_b["id"]

    # Verify that the task was moved with the project.
    response = client.get(f"{api_prefix}/tasks/{task['id']}")
    assert response.status_code == 200
    moved_task: dict[str, Any] = response.json()
    assert moved_task["group_id"] == group_b["id"]
    assert moved_task["project_id"] == project["id"]


def test_delete_project_removes_tasks_by_default(
    client: TestClient, api_prefix: str
) -> None:
    """Deleting a project deletes its tasks by default."""

    # Create a group.
    group_response = client.post(
        f"{api_prefix}/groups",
        json={"name": "Personal"},
    )
    assert group_response.status_code == 201
    group: dict[str, Any] = group_response.json()

    # Create a project.
    project_response = client.post(
        f"{api_prefix}/projects",
        json={
            "name": "Website",
            "description": "Website project",
            "group_id": group["id"],
        },
    )
    assert project_response.status_code == 201
    project: dict[str, Any] = project_response.json()

    # Create a task assigned to the project.
    task_response = client.post(
        f"{api_prefix}/tasks",
        json={
            "title": "Homepage",
            "description": "Build it",
            "group_id": group["id"],
            "project_id": project["id"],
        },
    )
    assert task_response.status_code == 201
    task: dict[str, Any] = task_response.json()

    # Delete the project.
    response = client.delete(f"{api_prefix}/projects/{project['id']}")
    assert response.status_code == 200

    # Verify that both project and task were deleted.
    assert client.get(f"{api_prefix}/projects/{project['id']}").status_code == 404
    assert client.get(f"{api_prefix}/tasks/{task['id']}").status_code == 404


def test_delete_project_can_keep_tasks(client: TestClient, api_prefix: str) -> None:
    """Deleting a project can preserve its tasks without their assignment."""

    # Create a group.
    group_response = client.post(
        f"{api_prefix}/groups",
        json={"name": "Personal"},
    )
    assert group_response.status_code == 201
    group: dict[str, Any] = group_response.json()

    # Create a project.
    project_response = client.post(
        f"{api_prefix}/projects",
        json={
            "name": "Website",
            "description": "Website project",
            "group_id": group["id"],
        },
    )
    assert project_response.status_code == 201
    project: dict[str, Any] = project_response.json()

    # Create a task assigned to the project.
    task_response = client.post(
        f"{api_prefix}/tasks",
        json={
            "title": "Homepage",
            "description": "Build it",
            "group_id": group["id"],
            "project_id": project["id"],
        },
    )
    assert task_response.status_code == 201
    task: dict[str, Any] = task_response.json()

    # Delete the project while keeping its tasks.
    response = client.request(
        "DELETE",
        f"{api_prefix}/projects/{project['id']}",
        json={"keep_tasks": True},
    )
    assert response.status_code == 200

    # Verify that the project was deleted.
    assert client.get(f"{api_prefix}/projects/{project['id']}").status_code == 404

    # Verify that the task was preserved and unassigned.
    response = client.get(f"{api_prefix}/tasks/{task['id']}")
    assert response.status_code == 200
    preserved_task: dict[str, Any] = response.json()
    assert preserved_task["project_id"] is None
    assert preserved_task["group_id"] == group["id"]


def test_list_project_tasks(client: TestClient, api_prefix: str) -> None:
    """Get all tasks assigned to a project."""

    # Create a group.
    group_response = client.post(
        f"{api_prefix}/groups",
        json={"name": "Personal"},
    )
    assert group_response.status_code == 201
    group: dict[str, Any] = group_response.json()

    # Create a project.
    project_response = client.post(
        f"{api_prefix}/projects",
        json={
            "name": "Website",
            "description": "Website project",
            "group_id": group["id"],
        },
    )
    assert project_response.status_code == 201
    project: dict[str, Any] = project_response.json()

    # Create two tasks assigned to the project.
    task_1_response = client.post(
        f"{api_prefix}/tasks",
        json={
            "title": "Homepage",
            "description": "Build homepage",
            "group_id": group["id"],
            "project_id": project["id"],
        },
    )
    assert task_1_response.status_code == 201
    task_1: dict[str, Any] = task_1_response.json()

    task_2_response = client.post(
        f"{api_prefix}/tasks",
        json={
            "title": "About page",
            "description": "Build about page",
            "group_id": group["id"],
            "project_id": project["id"],
        },
    )
    assert task_2_response.status_code == 201
    task_2: dict[str, Any] = task_2_response.json()

    # Get all tasks assigned to the project.
    response = client.get(f"{api_prefix}/projects/{project['id']}/tasks")

    # Assert that both tasks are returned.
    assert response.status_code == 200
    tasks: list[dict[str, Any]] = response.json()
    assert {task["id"] for task in tasks} == {
        task_1["id"],
        task_2["id"],
    }
