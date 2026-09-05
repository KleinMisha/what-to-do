"""Request and response models for API"""

from uuid import UUID

from pydantic import BaseModel

from what_to_do.tasks.models import Group, Priority, Project, Task


# ------------
#   Tasks
# ------------
class TaskRequest(BaseModel):
    """For POST, PUT requests"""

    title: str
    group_id: UUID
    description: str
    priority: Priority | None = None
    project_id: UUID | None = None


class TaskGroupRequest(BaseModel):
    """When assigning to a different group."""

    group_id: UUID
    project_id: UUID | None = None


class TaskProjectRequest(BaseModel):
    """When assigning to a different project, within the same group."""

    project_id: UUID | None = None


class TaskResponse(TaskRequest):
    """Response for all endpoints returning Tasks"""

    id: UUID


def task_from_request(request: TaskRequest, *, task_id: UUID) -> Task:
    """Convert an incoming request to domain model required by service."""
    return Task(
        id=task_id,
        group_id=request.group_id,
        title=request.title,
        description=request.description,
        priority=request.priority,
        project_id=request.project_id,
    )


def task_to_response(task: Task) -> TaskResponse:
    """Convert domain model returned by service into response model."""
    return TaskResponse(
        id=task.id,
        title=task.title,
        group_id=task.group_id,
        description=task.description or "",
        priority=task.priority,
        project_id=task.project_id,
    )


# ------------
#   Projects
# ------------


class ProjectRequest(BaseModel):
    """For POST, PUT request."""

    name: str
    description: str
    group_id: UUID


class ProjectDeleteRequest(BaseModel):
    """
    Info needed to delete a project.
    Rule for underlying tasks.
    """

    keep_tasks: bool


class ProjectGroupRequest(BaseModel):
    """When assigning to a different group."""

    group_id: UUID


class ProjectResponse(ProjectRequest):
    """Response for all endpoints returning Projects."""

    id: UUID


def project_from_request(request: ProjectRequest, *, project_id: UUID) -> Project:
    """Convert an incoming request to domain model required by service."""
    return Project(
        id=project_id,
        group_id=request.group_id,
        name=request.name,
        description=request.description or None,
    )


def project_to_response(project: Project) -> ProjectResponse:
    """Convert domain model returned by service into response model."""
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description or "",
        group_id=project.group_id,
    )


# ------------
#   Groups
# ------------


class GroupRequest(BaseModel):
    """For POST, PUT requests."""

    name: str


class GroupResponse(GroupRequest):
    """Response for all endpoints returning Groups."""

    id: UUID


def group_from_request(request: GroupRequest, *, group_id: UUID) -> Group:
    """Convert an incoming request to domain model required by service."""
    return Group(id=group_id, name=request.name)


def group_to_response(group: Group) -> GroupResponse:
    """Convert domain model returned by service into response model."""
    return GroupResponse(id=group.id, name=group.name)
