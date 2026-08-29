"""
Domain level data models:
----
* Tasks contain a work item do be done
* Project is a group of tasks (related subject)
* ProjectGroup is a group of projects (work vs personal, etc.)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Protocol
from uuid import UUID


class Priority(Enum):
    HIGH = "high"
    LOW = "low"


class HasID(Protocol):
    "To facilitate defining generic type hints in other layers."

    id: UUID


class HasGroupID(Protocol):
    id: UUID
    group_id: UUID


@dataclass
class Task:
    """A work item."""

    id: UUID
    group_id: UUID
    title: str
    description: str | None = None
    priority: Priority | None = None
    project_id: UUID | None = None


@dataclass
class Project:
    """A container of multiple tasks."""

    id: UUID
    group_id: UUID
    name: str
    description: str | None = None


@dataclass
class Group:
    """Container for a collection of projects or tasks."""

    id: UUID
    name: str
