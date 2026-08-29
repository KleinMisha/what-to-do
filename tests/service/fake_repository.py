"""Fake, in-memory repository that manages a list of resource items."""

from uuid import UUID

from what_to_do.tasks.models import HasID


class FakeRepository[T: HasID]:
    """Repository that stores items in-memory in a simple list"""

    def __init__(self, items: list[T] | None = None) -> None:
        self.items = items or []

    def create(self, model: T) -> T:
        self.items.append(model)
        return model

    def get(self, id: UUID) -> T | None:
        return next(
            (item for item in self.items if item.id == id),
            None,
        )

    def delete(self, id: UUID) -> T | None:
        existing_resource = self.get(id)
        if existing_resource is None:
            return None
        self.items.remove(existing_resource)
        return existing_resource

    def update(self, model: T) -> T | None:
        existing_resource = self.get(model.id)
        if existing_resource is None:
            return None
        idx = self.items.index(existing_resource)
        self.items[idx] = model
        return model
