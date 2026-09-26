"""Command group: `config`"""

from pathlib import Path
from typing import Annotated

from typer import Argument, Exit, Option, Typer, echo

from what_to_do.cli.exceptions import CLIError, SettingsFileError
from what_to_do.cli.settings import (
    SETTINGS_FILE_PATH,
    configure_cli_setting,
    restore_defaults,
    show_cli_settings,
)

app = Typer(name="config", no_args_is_help=True)


@app.command("show")
def show_settings(
    file: Annotated[
        Path | None, Option("--file", "-f", help="TOML file with configuration.")
    ] = None,
    defaults: Annotated[
        bool, Option("--defaults", help="Include default configuration in output.")
    ] = False,
) -> None:
    """Display current configuration."""

    settings_file = file or SETTINGS_FILE_PATH
    show_cli_settings(settings_file, incl_defaults=defaults)
    raise Exit(code=0)


@app.command("set")
def set_setting(
    key: Annotated[str, Argument(help="Configuration to set.")],
    value: Annotated[str, Argument(help="Desired value.")],
    file: Annotated[
        Path | None, Option("--file", "-f", help="TOML file with configuration.")
    ] = None,
) -> None:
    """Configure a specific setting."""
    try:
        settings_file = file or SETTINGS_FILE_PATH
        configure_cli_setting(key, value, settings_path=settings_file)
        raise Exit(code=0)
    except CLIError as e:
        echo(f"{type(e).__name__} : {e!s}")
        raise Exit(code=1)


@app.command()
def reset(
    file: Annotated[
        Path | None, Option("--file", "-f", help="TOML file with configuration.")
    ] = None,
    dry_run: Annotated[
        bool, Option("--dry-run", help="Only print the file that will get deleted.")
    ] = False,
) -> None:
    """Restore default configuration."""
    try:
        settings_file = file or SETTINGS_FILE_PATH
        restore_defaults(settings_file, dry_run=dry_run)
        echo("Restored default configuration.")
        raise Exit(code=0)
    except SettingsFileError:
        echo("Already using default configuration.")
        raise Exit(code=0)
