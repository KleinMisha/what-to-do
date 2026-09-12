"""Abstraction for Client calling the Service(s)"""

from typing import Any, Protocol
from uuid import UUID


class Client[T](Protocol):
    """Defines the user-facing operations that can be done with a resource of type T

    CLI / TUI / etc. then becomes thin wrappers around the Client.

    Simplest version is a LocalClient which directly calls Service classes
    A RemoteClient invokes the API.
    """

    def get(self, id: UUID) -> T: ...
    def get_all(self) -> list[T]: ...
    def create(self, id: UUID, *args: Any, **kwargs: Any) -> T: ...
    def update(self, id: UUID, *args: Any, **kwargs: Any) -> T: ...
    def delete(self, id: UUID) -> T: ...
