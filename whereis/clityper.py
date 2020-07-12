import typer
from pathlib import Path
from whereis import utils

app: typer.Typer = typer.Typer()


@app.command()
def find(
    name: str,
    database_location: Path = typer.Argument(
        utils.config_folder(), help="The location of the database."
    ),
) -> None:
    """Find an entry."""


@app.command()
def entry(
    name: str = typer.Option(..., help="The name of the entry."),
    database_location: Path = typer.Argument(
        utils.config_folder(), help="The location of the database."
    ),
    info: bool = typer.Argument(True, help="Show information about the entry."),
    add: bool = typer.Argument(False, help="Add the entry to the database."),
    remove: bool = typer.Argument(False, help="Remove the entry from the database."),
) -> None:
    """Query, add and remove entries."""


def main() -> None:
    return app()
