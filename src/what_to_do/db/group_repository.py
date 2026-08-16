"""A SQL repository for Group resource"""

from what_to_do.db.repository import Repository
from what_to_do.db.schema import DBGroup
from what_to_do.tasks.models import Group


class GroupRepository(Repository[Group, DBGroup]):
    """SQL database repository for Groups. Implements 'Repository"""

    db_model = DBGroup

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

    def _update_fields(self, db_entry: DBGroup, new_data: Group) -> DBGroup:
        db_entry.name = new_data.name
        return db_entry
