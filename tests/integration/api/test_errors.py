from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from what_to_do.api.errors import ERROR_STATUS_CODES
from what_to_do.core.exceptions import (
    InvalidAssignmentError,
    ResourceNotFoundError,
)


@pytest.mark.parametrize(
    ("url"),
    [
        "/api/v1/groups",
        "/api/v1/projects",
        "/api/v1/tasks",
    ],
)
def test_missing_resource_returns_404(
    client: TestClient,
    url: str,
) -> None:
    """Return 404 when requesting a nonexistent resource."""

    response = client.get(f"{url}/{uuid4()}")

    assert response.status_code == ERROR_STATUS_CODES[ResourceNotFoundError]
    assert response.json()["error"] == ResourceNotFoundError.__name__


def test_task_cannot_use_missing_group(client: TestClient) -> None:
    """Return 404 when creating a task with a nonexistent group."""

    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Task",
            "description": "Description",
            "group_id": str(uuid4()),
            "project_id": None,
        },
    )

    assert response.status_code == ERROR_STATUS_CODES[ResourceNotFoundError]
    assert response.json()["error"] == ResourceNotFoundError.__name__


def test_task_cannot_use_missing_project(client: TestClient) -> None:
    """Return 404 when creating a task with a nonexistent project."""

    # Create a valid group.
    group_response = client.post(
        "/api/v1/groups",
        json={"name": "Personal"},
    )
    assert group_response.status_code == 201
    group: dict[str, Any] = group_response.json()

    # Attempt to create a task with a nonexistent project.
    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Task",
            "description": "Description",
            "group_id": group["id"],
            "project_id": str(uuid4()),
        },
    )

    assert response.status_code == ERROR_STATUS_CODES[ResourceNotFoundError]
    assert response.json()["error"] == ResourceNotFoundError.__name__


def test_task_cannot_use_project_from_different_group(
    client: TestClient,
) -> None:
    """Return 409 when a task and project belong to different groups."""

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

    # Create a project in group B.
    project_response = client.post(
        "/api/v1/projects",
        json={
            "name": "Project",
            "description": "Project description",
            "group_id": group_b["id"],
        },
    )
    assert project_response.status_code == 201
    project: dict[str, Any] = project_response.json()

    # Attempt to create a task in group A using the project from group B.
    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Task",
            "description": "Description",
            "group_id": group_a["id"],
            "project_id": project["id"],
        },
    )

    assert response.status_code == ERROR_STATUS_CODES[InvalidAssignmentError]
    assert response.json()["error"] == InvalidAssignmentError.__name__


def test_invalid_uuid_returns_422(client: TestClient) -> None:
    """Return 422 when a path parameter is not a valid UUID."""

    response = client.get("/api/v1/tasks/not-a-uuid")

    assert response.status_code == 422


def test_missing_required_field_returns_422(client: TestClient) -> None:
    """Return 422 when a required request field is missing."""

    response = client.post(
        "/api/v1/groups",
        json={},
    )

    assert response.status_code == 422
