"""Local client bypasses the API and directly calls the Service's"""

from typing import Any, Protocol
from uuid import UUID


class CRUDService[T](Protocol):
    """Basic CRUD capabilities all the resource services have."""

    def create(self, resource: T, /) -> T: ...
    def get(self, id: UUID, /) -> T: ...
    def get_all(self) -> list[T]: ...
    def update_info(self, resource: T, /) -> T: ...
    def delete(self, id: UUID, /) -> T: ...


class LocalClient[T]:
    """
    Client that invokes services directly.

    implements CRUD operations common for all resources.

    Used by CLI / TUI (in local configuration mode).
    Thin wrapper around the service, but allows for easy extension to a remote client.
    """

    def __init__(self, service: CRUDService[T], resource_type: type[T]) -> None:
        self.service = service
        self.resource_type = resource_type

    def get(self, id: UUID) -> T:
        return self.service.get(id)

    def get_all(self) -> list[T]:
        return self.service.get_all()

    def delete(self, id: UUID) -> T:
        return self.service.delete(id)

    def create(self, id: UUID, **attributes: Any) -> T:
        resource_class: Any = self.resource_type
        resource = resource_class(id=id, **attributes)
        return self.service.create(resource)

    def update(self, id: UUID, **attributes: Any) -> T:
        resource_class: Any = self.resource_type
        resource = resource_class(id=id, **attributes)
        return self.service.update_info(resource)
