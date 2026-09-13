"""Helpers used by multiple command groups."""

from what_to_do.tasks.models import Group, Project, Task

# todo: adjust once settled on the actual tool name
TOOL_NAME = "what-to-do"


def render_group(group: Group) -> str:
    """Render a string with Task information."""

    # TODO make information more rich. Include options to show more / less
    return f"[{group.id}] \t {group.name}"


def render_task(task: Task) -> str:
    """Render a string with Task information."""

    # TODO make information more rich. Include options to show more / less
    return f"[{task.id}] \t {task.title}"


def render_project(project: Project) -> str:
    """Render a string with Project information."""

    # TODO make information more rich. Include options to show more / less
    return f"[{project.id}] \t {project.name}"
