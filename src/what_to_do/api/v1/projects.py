"""
Router for project endpoints.
common prefix set in server / FastAPI construction.
"""

from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from what_to_do.api.v1.models import (
    ProjectDeleteRequest,
    ProjectGroupRequest,
    ProjectRequest,
    ProjectResponse,
    TaskResponse,
    project_from_request,
    project_to_response,
    task_to_response,
)
from what_to_do.db.database import get_db
from what_to_do.db.group_repository import GroupRepository
from what_to_do.db.project_repository import ProjectRepository
from what_to_do.db.task_repository import TaskRepository
from what_to_do.service.project_service import ProjectService

router = APIRouter(tags=["Projects"])


def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    """Setup dependency injection using FastAPI."""
    task_repo = TaskRepository(db)
    project_repo = ProjectRepository(db)
    group_repo = GroupRepository(db)
    return ProjectService(
        tasks=task_repo,
        projects=project_repo,
        groups=group_repo,
    )


@router.get("", response_model=list[ProjectResponse], status_code=status.HTTP_200_OK)
def get_all_tasks(
    service: ProjectService = Depends(get_project_service),
) -> list[ProjectResponse]:
    """Fetch all tasks stored"""
    projects = service.get_all()
    return [project_to_response(project) for project in projects]


@router.get(
    "/{project_id}", response_model=ProjectResponse, status_code=status.HTTP_200_OK
)
def get_project(
    project_id: UUID, service: ProjectService = Depends(get_project_service)
) -> ProjectResponse:
    """Get a project by it's ID"""
    project = service.get(project_id)
    return project_to_response(project)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    request: ProjectRequest,
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    """Create a new project"""
    new_id = uuid4()
    project = project_from_request(request, project_id=new_id)
    created = service.create(project)
    return project_to_response(created)


@router.put(
    "/{project_id}", response_model=ProjectResponse, status_code=status.HTTP_200_OK
)
def update_project(
    project_id: UUID,
    request: ProjectRequest,
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    """Update a Project's data"""
    before_update = project_from_request(request, project_id=project_id)
    after_update = service.update_info(before_update)
    return project_to_response(after_update)


@router.delete(
    "/{project_id}", response_model=ProjectResponse, status_code=status.HTTP_200_OK
)
def delete_project(
    project_id: UUID,
    request: ProjectDeleteRequest,
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    """Delete a project"""
    project = service.delete(project_id, keep_tasks=request.keep_tasks)
    return project_to_response(project)


@router.patch(
    "/{project_id}/group",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
)
def change_project_level_group(
    project_id: UUID,
    request: ProjectGroupRequest,
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    """Assign project to a different group"""
    before_update = service.get(project_id)
    after_update = service.assign_to_new_group(before_update, group_id=request.group_id)
    return project_to_response(after_update)


@router.get(
    "/{project_id}/tasks",
    response_model=list[TaskResponse],
    status_code=status.HTTP_200_OK,
)
def get_tasks(
    project_id: UUID, service: ProjectService = Depends(get_project_service)
) -> list[TaskResponse]:
    """list all tasks assigned to a given project"""
    tasks = service.list_tasks(project_id)
    return [task_to_response(task) for task in tasks]
