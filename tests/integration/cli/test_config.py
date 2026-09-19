"""Managing CLI configuration"""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from what_to_do.cli.entrypoint import app
from what_to_do.cli.settings import (
    CLISettings,
    get_cli_settings,
    get_default_cli_settings,
)


@pytest.fixture
def config_path(tmp_path: Path) -> Path:
    """Temporary config file for tests"""
    return tmp_path / "config.toml"


def test_show_current_settings(config_path: Path, cli_client: CliRunner) -> None:
    """Display settings with default values"""
    # populate config file:
    config_path.write_text(
        "client_mode = 'remote'\n"
        "api_url = 'https://todo.example.com'\n"
        "database_filename = 'work.db'\n"
    )

    # expected current settings
    current = get_cli_settings(settings_path=config_path)

    # display the settings
    result = cli_client.invoke(app, ["config", "show", "--file", str(config_path)])
    assert result.exit_code == 0

    # validate output
    assert "Current settings" in result.stdout
    assert current.model_dump_json() in result.stdout
    assert "Default settings" not in result.stdout


def test_show_settings_and_defaults(config_path: Path, cli_client: CliRunner) -> None:
    """Display both current and default settings"""
    # populate config file:
    config_path.write_text(
        "client_mode = 'remote'\n"
        "api_url = 'https://todo.example.com'\n"
        "database_filename = 'work.db'\n"
    )

    # current config
    current = get_cli_settings(settings_path=config_path)

    # default configuration
    defaults = get_default_cli_settings()

    # display the settings
    result = cli_client.invoke(
        app, ["config", "show", "-f", str(config_path), "--defaults"]
    )
    assert result.exit_code == 0

    # validate output
    assert "Current settings" in result.stdout
    assert current.model_dump_json() in result.stdout
    assert "Default settings" in result.stdout
    assert defaults.model_dump_json() in result.stdout


def test_current_settings_are_defaults_if_no_file_exists(
    config_path: Path,
    cli_client: CliRunner,
) -> None:
    """Display configuration without writing anything to file"""

    # confirm that no configuration file exists
    assert not config_path.exists()

    # expected configurations
    current = get_cli_settings(settings_path=config_path)
    defaults = get_default_cli_settings()
    assert current == defaults

    result = cli_client.invoke(
        app, ["config", "show", "-f", str(config_path), "--defaults"]
    )

    assert result.exit_code == 0

    assert "Current settings" in result.stdout
    assert "Default settings" in result.stdout
    assert result.stdout.count(defaults.model_dump_json()) == 2


def test_set_setting(cli_client: CliRunner, config_path: Path) -> None:
    """Modify a setting"""

    # modify
    result = cli_client.invoke(
        app,
        ["config", "set", "database_filename", "new_name.db", "-f", str(config_path)],
    )
    assert result.exit_code == 0

    # validate modification
    persisted_config = get_cli_settings(settings_path=config_path)
    assert persisted_config.database_filename == "new_name.db"

    # validate that other settings are still defaults
    defaults = get_default_cli_settings()
    assert persisted_config.client_mode == defaults.client_mode
    assert persisted_config.remote_api_url == defaults.remote_api_url


def test_reset(cli_client: CliRunner, config_path: Path) -> None:
    """Restore defaults"""
    # modify
    result = cli_client.invoke(
        app,
        ["config", "set", "database_filename", "new_name.db", "-f", str(config_path)],
    )
    assert result.exit_code == 0

    # reset to defaults
    result = cli_client.invoke(app, ["config", "reset", "-f", str(config_path)])
    assert not config_path.exists()

    defaults = get_default_cli_settings()
    actual_config = get_cli_settings(settings_path=config_path)
    assert actual_config == defaults


def test_reset_dry_run(cli_client: CliRunner, config_path: Path) -> None:
    """Dry run: only display actions without actually affecting the file system"""

    # modify to write something to the file
    result = cli_client.invoke(
        app,
        ["config", "set", "database_filename", "new_name.db", "-f", str(config_path)],
    )
    assert result.exit_code == 0

    # execute dry run
    result = cli_client.invoke(
        app, ["config", "reset", "--dry-run", "-f", str(config_path)]
    )
    assert result.exit_code == 0
    assert str(config_path) in result.stdout
    assert config_path.exists()


def test_reset_when_already_default_config(
    cli_client: CliRunner, config_path: Path
) -> None:
    """Resetting to default values when these are already in-use should simply proceed with a simple message being displayed."""

    # confirm that no configuration file exists
    assert not config_path.exists()

    # perform reset
    result = cli_client.invoke(app, ["config", "reset", "-f", str(config_path)])
    assert result.exit_code == 0
    assert "Already using default configuration." in result.stdout


def test_set_setting_invalid_key(cli_client: CliRunner, config_path: Path) -> None:
    """Attempt to configure a non-existing setting"""

    result = cli_client.invoke(
        app,
        ["config", "set", "does_not_exist", "irrelevant_value", "-f", str(config_path)],
    )
    assert result.exit_code == 1
    assert "does_not_exist" in result.stdout


def test_set_setting_invalid_value(cli_client: CliRunner, config_path: Path) -> None:
    """Attempt to configure an invalid value"""

    result = cli_client.invoke(
        app, ["config", "set", "client_mode", "42", "-f", str(config_path)]
    )
    assert result.exit_code == 1
    assert "client_mode" in result.stdout
    assert "42" in result.stdout
    assert str(CLISettings.model_fields["client_mode"].annotation) in result.stdout


# def test_set_setting_invalid_value(
#     cli_runner: CliRunner,
#     tmp_path: Path,
# ) -> None:
#     config_path = tmp_path / "settings.toml"

#     result = cli_runner.invoke(
#         app,
#         [
#             "set",
#             "client_mode",
#             "invalid",
#             "--file",
#             str(config_path),
#         ],
#     )

#     assert result.exit_code == 1
#     assert "Invalid value" in result.output


# def test_reset_dry_run(
#     cli_runner: CliRunner,
#     tmp_path: Path,
# ) -> None:
#     config_path = tmp_path / "settings.toml"
#     config_path.write_text("client_mode = 'remote'\n")

#     result = cli_runner.invoke(
#         app,
#         ["reset", "--file", str(config_path), "--dry-run"],
#     )

#     assert result.exit_code == 0, result.output
#     assert str(config_path) in result.output
#     assert config_path.exists()
