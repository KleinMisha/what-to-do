import pytest

from tests.client.fakes import FakeLocalService, FakeResource
from what_to_do.client.local_client import LocalClient


@pytest.fixture
def fake_local_service() -> FakeLocalService[FakeResource]:
    return FakeLocalService[FakeResource]()


@pytest.fixture
def fake_local_client(
    fake_local_service: FakeLocalService[FakeResource],
) -> LocalClient[FakeResource]:
    return LocalClient(
        service=fake_local_service,
        resource_type=FakeResource,
    )
