"""Construction of Service: inject dependency on repository"""

from sqlalchemy.orm import Session

from what_to_do.db.group_repository import GroupRepository
from what_to_do.db.project_repository import ProjectRepository
from what_to_do.db.task_repository import TaskRepository
from what_to_do.service.group_service import GroupService
from what_to_do.service.project_service import ProjectService
from what_to_do.service.task_service import TaskService


def create_task_service(db: Session) -> TaskService:
    """Connect / inject repositories to construct TaskService."""
    task_repo = TaskRepository(db)
    project_repo = ProjectRepository(db)
    group_repo = GroupRepository(db)
    return TaskService(
        tasks=task_repo,
        projects=project_repo,
        groups=group_repo,
    )


def create_project_service(db: Session) -> ProjectService:
    """Connect / inject repositories to construct ProjectService."""
    task_repo = TaskRepository(db)
    project_repo = ProjectRepository(db)
    group_repo = GroupRepository(db)
    return ProjectService(
        tasks=task_repo,
        projects=project_repo,
        groups=group_repo,
    )


def create_group_service(db: Session) -> GroupService:
    """Connect / inject repositories to construct GroupService."""
    task_repo = TaskRepository(db)
    project_repo = ProjectRepository(db)
    group_repo = GroupRepository(db)
    return GroupService(
        tasks=task_repo,
        projects=project_repo,
        groups=group_repo,
    )
