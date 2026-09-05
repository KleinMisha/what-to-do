"""
Router for task endpoints.
common prefix set in server / FastAPI construction.
"""

from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from what_to_do.api.v1.models import (
    TaskGroupRequest,
    TaskProjectRequest,
    TaskRequest,
    TaskResponse,
    task_from_request,
    task_to_response,
)
from what_to_do.db.database import get_db
from what_to_do.db.group_repository import GroupRepository
from what_to_do.db.project_repository import ProjectRepository
from what_to_do.db.task_repository import TaskRepository
from what_to_do.service.task_service import TaskService

router = APIRouter(tags=["Tasks"])


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    """Setup dependency injection using FastAPI."""
    task_repo = TaskRepository(db)
    project_repo = ProjectRepository(db)
    group_repo = GroupRepository(db)
    return TaskService(
        tasks=task_repo,
        projects=project_repo,
        groups=group_repo,
    )


@router.get("", response_model=list[TaskResponse], status_code=status.HTTP_200_OK)
def get_all_tasks(
    service: TaskService = Depends(get_task_service),
) -> list[TaskResponse]:
    """Fetch all tasks stored"""
    tasks = service.get_all()
    return [task_to_response(task) for task in tasks]


@router.get("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def get_task(
    task_id: UUID,
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    """Get a task by its ID."""
    task = service.get(task_id)
    return task_to_response(task)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    request: TaskRequest,
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    """Create a new Task"""
    new_id = uuid4()
    task = task_from_request(request, task_id=new_id)
    created = service.create(task)
    return task_to_response(created)


@router.put("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def update_task(
    task_id: UUID,
    request: TaskRequest,
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    """Update a Task's data"""
    before_update = task_from_request(request, task_id=task_id)
    after_update = service.update_info(before_update)
    return task_to_response(after_update)


@router.delete(
    "/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK
)
def delete_task(
    task_id: UUID,
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    """Delete a task"""
    task = service.delete(task_id)
    return task_to_response(task)


@router.patch(
    "/{task_id}/group",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
)
def change_task_level_group(
    task_id: UUID,
    request: TaskGroupRequest,
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    """Assign a task to a new group. Optionally assign it to a project within that group."""
    before_update = service.get(task_id)
    after_update = service.assign(
        task=before_update,
        group_id=request.group_id,
        project_id=request.project_id,
    )
    return task_to_response(after_update)


@router.patch(
    "/{task_id}/project",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
)
def change_task_level_project(
    task_id: UUID,
    request: TaskProjectRequest,
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    """Assign a task to a new project or unassign from a project. Always staying within the same group"""
    before_update = service.get(task_id)
    after_update = service.assign(
        task=before_update,
        group_id=before_update.group_id,
        project_id=request.project_id,
    )
    return task_to_response(after_update)
