"""A SQL repository for Tasks"""

from uuid import UUID

from sqlalchemy import select

from what_to_do.db.repository import Repository
from what_to_do.db.schema import DBTask
from what_to_do.tasks.models import Task


class TaskRepository(Repository[Task, DBTask]):
    """SQL database repository for Tasks. Implements 'Repository'"""

    db_model = DBTask

    def get_by_project_id(self, project_id: UUID) -> list[DBTask]:
        """Get all tasks assigned to a given project."""
        query = select(self.db_model).where(self.db_model.project_id == project_id)
        return list(self.db.scalars(query).all())

    def get_by_group_id(self, group_id: UUID) -> list[DBTask]:
        """Get all tasks assigned to a given group."""
        query = select(self.db_model).where(self.db_model.group_id == group_id)
        return list(self.db.scalars(query).all())

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

    def _update_fields(self, db_entry: DBTask, new_data: Task) -> DBTask:
        db_entry.title = new_data.title
        db_entry.description = new_data.description
        db_entry.priority = new_data.priority
        db_entry.group_id = new_data.group_id
        db_entry.project_id = new_data.project_id
        return db_entry
