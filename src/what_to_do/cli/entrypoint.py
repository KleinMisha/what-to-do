from typer import Typer, echo

app = Typer(no_args_is_help=True)


@app.command()
def hello() -> None:
    """Say hello"""
    echo("Hello from what-to-do!")


def main() -> None:
    """What To Do CLI entrypoint."""
    app()


if __name__ == "__main__":
    main()
