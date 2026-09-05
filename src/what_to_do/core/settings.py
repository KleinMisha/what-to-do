"""Shared configuration."""

from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class WhatToDoSettings(BaseSettings):
    """Global application configuration."""

    app_name: str = "what-to-do"
    backend_port: int = 8000
    backend_api_version: str = "v1"
    db_name: str = "my_tasks.db"

    @property
    def db_url(self) -> str:
        """Place database file in project root."""
        base_dir = Path(__file__)
        project_root = base_dir.parent.parent.parent.parent
        return f"sqlite:///{project_root / 'db' / self.db_name}"

    @property
    def api_url_prefix(self) -> str:
        """Common part of API's URL."""
        return f"/api/{self.backend_api_version}"


def get_settings() -> WhatToDoSettings:
    """Expose settings so they can be imported elsewhere"""
    return WhatToDoSettings()
