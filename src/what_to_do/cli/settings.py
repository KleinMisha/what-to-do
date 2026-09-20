"""
CLI specific configuration. Values set in TOML file stored locally.

Not environment variables.
Hence, using 'vanilla' pydantic BaseModel rather than pydantic-settings model.
"""

import tomllib
from pathlib import Path
from shutil import rmtree
from typing import Any

import tomli_w
from pydantic import BaseModel, ValidationError

from what_to_do.cli.exceptions import (
    InvalidSettingsKeyError,
    InvalidSettingsValueError,
    SettingsFileError,
)
from what_to_do.client.factory import ClientMode

SETTINGS_DIR = Path().home() / ".config" / "what-to-do"
SETTINGS_FILE_PATH = SETTINGS_DIR / "config.toml"
DB_DIR = Path().home() / ".local" / "share" / "what-to-do"


class CLISettings(BaseModel):
    client_mode: ClientMode = ClientMode.LOCAL
    database_filename: str = "what_to_do.db"
    remote_api_url: str = "http://localhost:8000"  # NOTE: Only used with remote host/client. Hence, only relevant later.

    @property
    def database_path(self) -> Path:
        """path to database file"""
        return DB_DIR / self.database_filename


def get_cli_settings(settings_path: Path = SETTINGS_FILE_PATH) -> CLISettings:
    """Load CLI settings from defaults or TOML"""

    file_settings: dict[str, Any] = {}

    if settings_path.exists():
        with settings_path.open("rb") as file:
            file_settings = tomllib.load(file)

    return CLISettings(**file_settings)


def get_default_cli_settings() -> CLISettings:
    """Default CLI configuration."""
    return CLISettings()


def save_cli_settings(
    settings: CLISettings, settings_file: Path = SETTINGS_FILE_PATH
) -> None:
    """write settings to file"""

    with settings_file.open("wb") as file:
        tomli_w.dump(settings.model_dump(mode="json"), file)

    print(f"Wrote settings into {settings_file!s}")


def show_cli_settings(
    settings_path: Path = SETTINGS_FILE_PATH, incl_defaults: bool = False
) -> None:
    """Display current settings"""

    print("==== Current settings ====")
    settings = get_cli_settings(settings_path)
    print(settings.model_dump_json())

    if incl_defaults:
        print("==== Default settings ====")
        defaults = get_default_cli_settings()
        print(defaults.model_dump_json())


def configure_cli_setting(
    key: str, value: str, settings_path: Path = SETTINGS_FILE_PATH
) -> CLISettings:
    """adjust value in settings"""
    # Validate the key is the name of an existing setting
    if key not in CLISettings.model_fields:
        raise InvalidSettingsKeyError(key, available_keys=set(CLISettings.model_fields))
    # get the current settings
    original_settings = get_cli_settings(settings_path)

    # update the settings (if valid value given data model)
    try:
        settings = original_settings.model_dump()
        settings[key] = value
        updated_settings = CLISettings.model_validate(settings)
    except ValidationError as e:
        expected_type = CLISettings.model_fields[key].annotation
        raise InvalidSettingsValueError(key, value, expected_type=expected_type) from e

    # write updated settings
    save_cli_settings(updated_settings, settings_path)

    print(f"Updated {key} to {value}")

    return updated_settings


def restore_defaults(
    settings_file: Path = SETTINGS_FILE_PATH, dry_run: bool = False
) -> None:
    """Restore default values by deleting the file.
    The `get_cli_settings()` method will then default to instantiating the class with default values"""

    if dry_run:
        print(f"[DRY-RUN] Would delete {settings_file!s}")
        return

    if not settings_file.exists():
        raise SettingsFileError(
            f"No persisted settings found. \n Expected location: {settings_file!s}"
        )

    settings_file.unlink(missing_ok=True)
    print(f"Deleted {settings_file!s}")


def delete_settings_dir(
    settings_dir: Path = SETTINGS_DIR, dry_run: bool = False
) -> None:
    """Delete the directory."""

    if dry_run:
        print(f"[DRY-RUN] Would delete {settings_dir!s}")
        return

    if not settings_dir.exists():
        raise SettingsFileError(f"No directory found: {settings_dir!s}")

    rmtree(settings_dir)
    print(f"Deleted {settings_dir!s}")


# def delete_database(dry_run: bool = False) -> None:
#     """Delete the local database"""
#     settings = get_cli_settings()
#     db_file = settings.database_path
#     if dry_run:
#         print(f"[DRY-RUN] Would delete {db_file!s}")
#         return

#     if not db_file.exists():
#         raise SettingsFileError(
#             f"No local database found. \n Expected location: {db_file!s}"
#         )

#     print(f"Deleted {db_file!s}")


# def ensure_database_dir(db_dir: Path = DB_DIR) -> None:
#     """Create the local cli application data directory."""
#     db_dir.mkdir(parents=True, exist_ok=True)
#     print(f"Created {db_dir!s}")
