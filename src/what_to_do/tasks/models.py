"""
Domain level data models:
----
* Tasks contain a work item do be done
* Project is a group of tasks (related subject)
* ProjectGroup is a group of projects (work vs personal, etc.)
"""

from dataclasses import dataclass
from enum import Enum, auto
from uuid import UUID


class Priority(Enum):
    HIGH = auto()
    LOW = auto()


@dataclass
class Task:
    """A work item."""

    id: UUID
    group_id: UUID
    title: str
    description: str = ""
    priority: Priority | None = None
    project_id: UUID | None = None


@dataclass
class Project:
    """A container of multiple tasks."""

    id: UUID
    group_id: UUID
    name: str
    description: str = ""


@dataclass
class Group:
    """Container for a collection of projects or tasks."""

    id: UUID
    name: str
