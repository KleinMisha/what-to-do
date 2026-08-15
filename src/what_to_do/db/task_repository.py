"""A SQL repository for Tasks"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from what_to_do.db.schema import DBTask
from what_to_do.tasks.models import Task


class TaskRepository:
    """SQL database repository for Tasks. Implements 'Repository'"""

    def __init__(self, db_session: Session) -> None:
        self.db = db_session

    def create(self, model: Task) -> Task:
        """Create a new Task db model."""
        db_entry = self._to_db(model)
        self.db.add(db_entry)
        self.db.commit()
        self.db.refresh(db_entry)
        return self._to_domain(db_entry)

    def get(self, id: UUID) -> Task | None:
        """Get Task by id, if record exists."""
        db_entry = self._fetch_task_by_id(id)
        if not db_entry:
            return None
        return self._to_domain(db_entry)

    def update(self, model: Task) -> Task | None:
        """Overwrite database entry."""
        db_entry = self._fetch_task_by_id(model.id)
        if not db_entry:
            return None
        db_entry.title = model.title
        db_entry.description = model.description
        db_entry.priority = model.priority
        db_entry.group_id = model.group_id
        db_entry.project_id = model.project_id
        self.db.commit()
        self.db.refresh(db_entry)
        return self._to_domain(db_entry)

    def delete(self, id: UUID) -> Task | None:
        """Remove a Task's entry."""
        db_entry = self._fetch_task_by_id(id)
        if not db_entry:
            return None
        deleted_task = self._to_domain(db_entry)
        self.db.delete(db_entry)
        self.db.commit()
        return deleted_task

    def _to_db(self, model: Task) -> DBTask:
        """Convert into sqlmodel"""
        return DBTask(
            id=model.id,
            group_id=model.group_id,
            project_id=model.project_id,
            title=model.title,
            description=model.description,
            priority=model.priority,
        )

    def _to_domain(self, db_entry: DBTask) -> Task:
        return Task(
            id=db_entry.id,
            group_id=db_entry.group_id,
            project_id=db_entry.project_id,
            title=db_entry.title,
            description=db_entry.description,
            priority=db_entry.priority,
        )

    def _fetch_task_by_id(self, id: UUID) -> DBTask | None:
        """Find the Task, if it exists"""
        query = select(DBTask).where(DBTask.id == id)
        return self.db.execute(query).scalar_one_or_none()
