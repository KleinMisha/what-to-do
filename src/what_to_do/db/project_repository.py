"""A SQL repository for Project resource"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from what_to_do.db.schema import DBProject
from what_to_do.tasks.models import Project


class ProjectRepository:
    """A repository of objects T"""

    def __init__(self, db_session: Session) -> None:
        self.db = db_session

    def create(self, model: Project) -> Project:
        """Create a new Project db model."""
        db_entry = self._to_db(model)
        self.db.add(db_entry)
        self.db.commit()
        self.db.refresh(db_entry)
        return self._to_domain(db_entry)

    def get(self, id: UUID) -> Project | None:
        """Get Project by id, if record exists."""
        db_entry = self._fetch_project_by_id(id)
        if not db_entry:
            return None
        return self._to_domain(db_entry)

    def update(self, model: Project) -> Project | None:
        """Overwrite database entry."""
        db_entry = self._fetch_project_by_id(model.id)
        if not db_entry:
            return None
        db_entry.name = model.name
        db_entry.description = model.description
        db_entry.group_id = model.group_id
        self.db.commit()
        self.db.refresh(db_entry)
        return self._to_domain(db_entry)

    def delete(self, id: UUID) -> Project | None:
        """Remove a Project's entry."""
        db_entry = self._fetch_project_by_id(id)
        if not db_entry:
            return None
        deleted_project = self._to_domain(db_entry)
        self.db.delete(db_entry)
        self.db.commit()
        return deleted_project

    def _to_db(self, model: Project) -> DBProject:
        return DBProject(
            id=model.id,
            group_id=model.group_id,
            name=model.name,
            description=model.description,
        )

    def _to_domain(self, db_entry: DBProject) -> Project:
        return Project(
            id=db_entry.id,
            group_id=db_entry.group_id,
            name=db_entry.name,
            description=db_entry.description,
        )

    def _fetch_project_by_id(self, id: UUID) -> DBProject | None:
        """Find the Project, if it exists"""
        query = select(DBProject).where(DBProject.id == id)
        return self.db.execute(query).scalar_one_or_none()
