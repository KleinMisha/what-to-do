"""
TUI specific configuration. Values set in TOML file stored locally.

Not environment variables.
Hence, using 'vanilla' pydantic BaseModel rather than pydantic-settings model.
"""

import tomllib
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from what_to_do.client.factory import ClientMode

SETTINGS_DIR = Path().home() / ".config" / "what-to-do"
SETTINGS_FILE_PATH = SETTINGS_DIR / "config.toml"
DB_DIR = Path().home() / ".local" / "share" / "what-to-do"


class TUISettings(BaseModel):
    client_mode: ClientMode = ClientMode.LOCAL
    database_filename: str = "what_to_do.db"
    remote_api_url: str = "http://localhost:8000"  # NOTE: Only used with remote host/client. Hence, only relevant later.

    @property
    def database_path(self) -> Path:
        """path to database file"""
        return DB_DIR / self.database_filename

    @property
    def database_url(self) -> str:
        """construct database URL"""
        if self.client_mode == ClientMode.LOCAL:
            return f"sqlite:////{self.database_path}"
        else:
            raise NotImplementedError


def get_tui_settings(settings_path: Path = SETTINGS_FILE_PATH) -> TUISettings:
    """Load CLI settings from defaults or TOML"""

    file_settings: dict[str, Any] = {}

    if settings_path.exists():
        with settings_path.open("rb") as file:
            file_settings = tomllib.load(file)

    return TUISettings(**file_settings)
