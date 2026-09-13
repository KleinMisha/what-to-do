"""Test fixtures used for CLI (integration) tests."""

from collections.abc import Generator
from contextlib import contextmanager

import pytest
from sqlalchemy.orm import Session
from typer.testing import CliRunner


@pytest.fixture
def cli_client(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[CliRunner]:
    """
    Overwrite CLI's database session.
    Setup a test runner by manually overwriting / patching the database session.
    Otherwise identical to the production CLI.


    ---
    NOTE: Clients are already constructed using the db_session. A simple patch of `what_to_do.client.factory.db_session`
    is now equivalent of using FastAPI's `dependency_overrides[get_db]`.
    """

    @contextmanager
    def _override_db_session() -> Generator[Session]:
        yield db_session

    monkeypatch.setattr("what_to_do.client.factory.db_session", _override_db_session)

    # NOTE Monkeypatch does cleanup automatically --> No try/finally block needed.
    yield CliRunner()
