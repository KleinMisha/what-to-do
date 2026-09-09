"""Double-check that creation of a local Groups client works as intended.

#! REMOVE IF LocalGroupsClient ever becomes a thing more than LocalClient[Groups]
"""

from uuid import uuid4

from what_to_do.client.factory import local_client
from what_to_do.tasks.models import Group, ResourceType


def test_get_local_client_for_groups() -> None:
    with local_client(ResourceType.GROUPS) as client:
        group_id = uuid4()
        group = client.create(group_id, name="Test group")

    assert group == Group(id=group_id, name="Test group")
