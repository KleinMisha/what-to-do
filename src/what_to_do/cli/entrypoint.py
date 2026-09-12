from typer import Typer, echo

from what_to_do.cli.routing.groups import app as groups_app
from what_to_do.cli.routing.projects import app as projects_app
from what_to_do.cli.routing.tasks import app as tasks_app

app = Typer(no_args_is_help=True)
app.add_typer(
    tasks_app, name="tasks", help="Manage tasks - Primary items (lowest level)"
)
app.add_typer(projects_app, name="projects", help="Manage projects")
app.add_typer(groups_app, name="groups", help="Manage task/project groups")


def main() -> None:
    """What To Do CLI entrypoint."""
    app()


if __name__ == "__main__":
    main()
