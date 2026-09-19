from typer import Typer

from what_to_do.cli.routing.config import app as config_app
from what_to_do.cli.routing.groups import app as groups_app
from what_to_do.cli.routing.projects import app as projects_app
from what_to_do.cli.routing.tasks import app as tasks_app

app = Typer(no_args_is_help=True)
app.add_typer(tasks_app, name="tasks", help="Manage tasks")
app.add_typer(projects_app, name="projects", help="Manage projects")
app.add_typer(groups_app, name="groups", help="Manage task/project groups")
app.add_typer(config_app, name="config", help="CLI configuration")


def main() -> None:
    """What To Do CLI entrypoint."""
    app()


if __name__ == "__main__":
    main()
