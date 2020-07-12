import typer
from pathlib import Path
from whereis import utils

app: typer.Typer = typer.Typer()


@app.command()
def find(
    name: str = typer.Argument(..., help="The name of the entry."),
    database_location: Path = typer.Option(
        utils.config_folder(), help="The location of the database."
    ),
) -> None:
    """Find an entry with the name NAME"""


@app.command()
def entry(
    name: str = typer.Argument(..., help="The name of the entry."),
    database_location: Path = typer.Option(
        utils.config_folder(), help="The location of the database."
    ),
    info: bool = typer.Option(True, help="Show information about the entry."),
    add: bool = typer.Option(False, help="Add the entry to the database."),
    remove: bool = typer.Option(False, help="Remove the entry from the database."),
) -> None:
    """Query, add and remove the entry with the name NAME."""


def main() -> None:
    return app()
