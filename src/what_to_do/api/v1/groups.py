"""
Router for group endpoints.
common prefix set in server / FastAPI construction.
"""

from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from what_to_do.api.v1.models import (
    GroupRequest,
    GroupResponse,
    ProjectResponse,
    TaskResponse,
    group_from_request,
    group_to_response,
    project_to_response,
    task_to_response,
)
from what_to_do.db.database import get_db
from what_to_do.db.group_repository import GroupRepository
from what_to_do.db.project_repository import ProjectRepository
from what_to_do.db.task_repository import TaskRepository
from what_to_do.service.group_service import GroupService

router = APIRouter(tags=["Groups"])


def get_group_service(db: Session = Depends(get_db)) -> GroupService:
    """Setup dependency injection using FastAPI."""
    task_repo = TaskRepository(db)
    project_repo = ProjectRepository(db)
    group_repo = GroupRepository(db)
    return GroupService(
        tasks=task_repo,
        projects=project_repo,
        groups=group_repo,
    )


@router.get("/{group_id}", response_model=GroupResponse, status_code=status.HTTP_200_OK)
def get_group(
    group_id: UUID,
    service: GroupService = Depends(get_group_service),
) -> GroupResponse:
    """Get a group by it's ID"""
    group = service.get(group_id)
    return group_to_response(group)


@router.post("", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
def create_group(
    request: GroupRequest,
    service: GroupService = Depends(get_group_service),
) -> GroupResponse:
    """Create a new group"""
    new_id = uuid4()
    group = group_from_request(request, group_id=new_id)
    created = service.create(group)
    return group_to_response(created)


@router.put("/{group_id}", response_model=GroupResponse, status_code=status.HTTP_200_OK)
def update_group(
    group_id: UUID,
    request: GroupRequest,
    service: GroupService = Depends(get_group_service),
) -> GroupResponse:
    """Update a Group's data"""
    before_update = service.get(group_id)
    after_update = service.update_info(before_update)
    return group_to_response(after_update)


@router.delete(
    "/{group_id}", response_model=GroupResponse, status_code=status.HTTP_200_OK
)
def delete_group(
    group_id: UUID, service: GroupService = Depends(get_group_service)
) -> GroupResponse:
    """Delete group and all of it's projects and tasks"""
    group = service.delete(group_id)
    return group_to_response(group)


@router.get(
    "/{group_id}/projects",
    response_model=list[ProjectResponse],
    status_code=status.HTTP_200_OK,
)
def get_projects(
    group_id: UUID, service: GroupService = Depends(get_group_service)
) -> list[ProjectResponse]:
    """List all projects assigned to a given group"""
    projects = service.list_projects(group_id)
    return [project_to_response(project) for project in projects]


@router.get(
    "/{group_id}/tasks",
    response_model=list[TaskResponse],
    status_code=status.HTTP_200_OK,
)
def get_tasks(
    group_id: UUID, service: GroupService = Depends(get_group_service)
) -> list[TaskResponse]:
    """List all tasks assigned to a given group"""
    tasks = service.list_tasks(group_id)
    return [task_to_response(task) for task in tasks]
