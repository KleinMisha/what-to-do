"""A SQL repository for Project resource"""

from what_to_do.db.repository import Repository
from what_to_do.db.schema import DBProject
from what_to_do.tasks.models import Project


class ProjectRepository(Repository[Project, DBProject]):
    """SQL database repository for Projects. Implements 'Repository"""

    db_model = DBProject

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

    def _update_fields(self, db_entry: DBProject, new_data: Project) -> DBProject:
        db_entry.name = new_data.name
        db_entry.description = new_data.description
        db_entry.group_id = new_data.group_id
        return db_entry
