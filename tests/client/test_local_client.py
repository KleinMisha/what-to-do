"""Unit tests for src/what_to_do/client/local_client.py.

Test the generic parts / shared logic across resources.
"""

from uuid import uuid4

import pytest

from tests.client.fakes import FakeResource
from what_to_do.client.local_client import LocalClient
from what_to_do.core.exceptions import ResourceNotFoundError


def test_create(fake_local_client: LocalClient[FakeResource]) -> None:
    """Create resource: Make sure client parses individual arguments and returns domain model"""
    resource_id = uuid4()
    resource = fake_local_client.create(resource_id, name="Test")

    assert resource == FakeResource(id=resource_id, name="Test", description="")


def test_get(fake_local_client: LocalClient[FakeResource]) -> None:
    """Check that a domain model is returned"""
    resource_id = uuid4()

    fake_local_client.create(resource_id, name="Test", description="test details")

    resource = fake_local_client.get(resource_id)
    assert resource == FakeResource(
        id=resource_id, name="Test", description="test details"
    )


def test_get_all(fake_local_client: LocalClient[FakeResource]) -> None:
    """Listing multiple resources"""
    first_id = uuid4()
    second_id = uuid4()

    fake_local_client.create(id=first_id, name="First", description="First item")
    fake_local_client.create(id=second_id, name="Second", description="Second item")

    resources = fake_local_client.get_all()
    expected = [
        FakeResource(id=first_id, name="First", description="First item"),
        FakeResource(id=second_id, name="Second", description="Second item"),
    ]
    assert len(resources) == len(expected)
    assert all(resource in expected for resource in resources)


def test_update(fake_local_client: LocalClient[FakeResource]) -> None:
    """mutation should happen on domain model level."""
    resource_id = uuid4()

    fake_local_client.create(resource_id, name="Before")

    updated = fake_local_client.update(
        resource_id, name="After", description="now with description"
    )
    assert updated == FakeResource(
        id=resource_id, name="After", description="now with description"
    )

    assert fake_local_client.get(resource_id) == updated


def test_delete(fake_local_client: LocalClient[FakeResource]) -> None:
    """simple roundtrip"""
    resource_id = uuid4()

    fake_local_client.create(
        resource_id, name="disposable", description="destroy after reading"
    )

    deleted = fake_local_client.delete(resource_id)
    assert deleted == FakeResource(
        id=resource_id, name="disposable", description="destroy after reading"
    )

    with pytest.raises(ResourceNotFoundError):
        fake_local_client.get(resource_id)
