"""Fake resource + in-memory CRUD service operations."""

from dataclasses import dataclass
from uuid import UUID

from what_to_do.core.exceptions import ResourceNotFoundError
from what_to_do.tasks.models import HasID


@dataclass
class FakeResource:
    id: UUID
    name: str
    description: str = ""


class FakeLocalService[T: HasID]:
    """Fake, in-memory service that manages resource items."""

    def __init__(self, items: list[T] | None = None) -> None:
        self.items = items or []

    def create(self, resource: T) -> T:
        self.items.append(resource)
        return resource

    def get(self, id: UUID) -> T:
        resource = next(
            (item for item in self.items if item.id == id),
            None,
        )
        if resource is None:
            raise ResourceNotFoundError("resource", id)
        return resource

    def get_all(self) -> list[T]:
        return self.items

    def update_info(self, resource: T) -> T:
        existing_resource = self.get(resource.id)
        idx = self.items.index(existing_resource)
        self.items[idx] = resource
        return resource

    def delete(self, id: UUID) -> T:
        resource = self.get(id)
        self.items.remove(resource)
        return resource
