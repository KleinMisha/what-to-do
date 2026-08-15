"""A SQL repository for Group resource"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from what_to_do.db.schema import DBGroup
from what_to_do.tasks.models import Group


class GroupRepository:
    """A repository of objects T"""

    def __init__(self, db_session: Session) -> None:
        self.db = db_session

    def create(self, model: Group) -> Group:
        """Create a new Group db model."""
        db_entry = self._to_db(model)
        self.db.add(db_entry)
        self.db.commit()
        self.db.refresh(db_entry)
        return self._to_domain(db_entry)

    def get(self, id: UUID) -> Group | None:
        """Get Group by id, if record exists."""
        db_entry = self._fetch_Group_by_id(id)
        if not db_entry:
            return None
        return self._to_domain(db_entry)

    def update(self, model: Group) -> Group | None:
        """Overwrite database entry."""
        db_entry = self._fetch_Group_by_id(model.id)
        if not db_entry:
            return None
        db_entry.name = model.name
        self.db.commit()
        self.db.refresh(db_entry)
        return self._to_domain(db_entry)

    def delete(self, id: UUID) -> Group | None:
        """Remove a Group's entry."""
        db_entry = self._fetch_Group_by_id(id)
        if not db_entry:
            return None
        deleted_Group = self._to_domain(db_entry)
        self.db.delete(db_entry)
        self.db.commit()
        return deleted_Group

    def _to_db(self, model: Group) -> DBGroup:
        return DBGroup(
            id=model.id,
            name=model.name,
        )

    def _to_domain(self, db_entry: DBGroup) -> Group:
        return Group(
            id=db_entry.id,
            name=db_entry.name,
        )

    def _fetch_Group_by_id(self, id: UUID) -> DBGroup | None:
        """Find the Group, if it exists"""
        query = select(DBGroup).where(DBGroup.id == id)
        return self.db.execute(query).scalar_one_or_none()
