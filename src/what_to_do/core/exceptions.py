"""Custom exceptions."""

from uuid import UUID


class ResourceNotFoundError(Exception):
    def __init__(self, resource: str, id: UUID) -> None:
        super().__init__(f"{resource.capitalize()} with id {id} not found.")


class InvalidAssignmentError(Exception):
    """When project / group assignments violate business logic."""
