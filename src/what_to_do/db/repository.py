"""Base Repository for any of the domain objects / resources"""

from abc import ABC, abstractmethod
from typing import Protocol, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

DomainModel = TypeVar("DomainModel")
DBModel = TypeVar("DBModel")


class HasID(Protocol):
    id: UUID


class Repository[DomainModel: HasID, DBModel](ABC):
    """A generic SQL Alchemy model"""

    db_model: type[DBModel]

    def __init__(self, db_session: Session) -> None:
        """Inject dependency: A resource needs a database connection."""
        self.db = db_session

    def create(self, model: DomainModel) -> DomainModel:
        """Create new resource entry."""
        db_entry = self._to_db(model)
        self.db.add(db_entry)
        self.db.commit()
        self.db.refresh(db_entry)
        return self._to_domain(db_entry)

    def get(self, id: UUID) -> DomainModel | None:
        """Get resource from database by ID, if it exists."""
        db_entry = self._fetch_by_id(id)
        if not db_entry:
            return None
        return self._to_domain(db_entry)

    def update(self, model: DomainModel) -> DomainModel | None:
        """Update an existing resource, if it exists."""
        original_entry = self._fetch_by_id(model.id)
        if not original_entry:
            return None

        updated_entry = self._update_fields(original_entry, model)
        self.db.commit()
        self.db.refresh(updated_entry)
        return self._to_domain(updated_entry)

    def delete(self, id: UUID) -> DomainModel | None:
        """Remove a resource's entry."""
        db_entry = self._fetch_by_id(id)
        if not db_entry:
            return None
        deleted_task = self._to_domain(db_entry)
        self.db.delete(db_entry)
        self.db.commit()
        return deleted_task

    def _fetch_by_id(self, id: UUID) -> DBModel:
        """Find the entry, if it exists"""
        query = select(self.db_model).where(self.db_model.id == id)  # type: ignore
        return self.db.execute(query).scalar_one_or_none()  # type: ignore

    @abstractmethod
    def _to_db(self, model: DomainModel) -> DBModel: ...

    @abstractmethod
    def _to_domain(self, db_entry: DBModel) -> DomainModel: ...

    @abstractmethod
    def _update_fields(self, db_entry: DBModel, new_data: DomainModel) -> DBModel:
        """Update fields in an already existing DBModel."""
