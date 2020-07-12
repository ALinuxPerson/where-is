import typer
from pathlib import Path
from whereis import utils, levels, Database, Entry
from typing import Optional, List
import os
from rich.table import Table
from rich import print

app: typer.Typer = typer.Typer(
    help="An elegant way to find configuration files (and folders)."
)
is_verbose: bool = False


def _log(message: str) -> None:
    try:
        return levels.debug(message) if is_verbose else None
    except (ValueError, TypeError):
        levels.error(f"WIS_VERBOSE isn't a valid boolean.")


def _get_entry(entry_name: str, database: Database) -> Optional[Entry]:
    for entry_ in database.entries:
        _log(f"Checking if [bold]'{entry_.name}'[/] == [bold]'{entry_name}'[/]...")
        if entry_.name == entry_name:
            _log(f"Got entry, {entry_}")
            return entry_
    else:
        levels.error(f"Couldn't find entry '{entry_name}' in the database.")
        return None


def _gen_entry_table(entry_: Entry) -> Table:
    columns: List[str] = ["Locations", "Exists", "Is File", "Is Folder"]
    table: Table = Table(title="[bold purple]Config files found")
    for column in columns:
        table.add_column(column)
    for location, exists in entry_.locations_exists().items():
        formatted_location: str = f"[magenta]{location}"
        formatted_exists: str = f"[red]{exists}" if not exists else f"[green4]{exists}"
        is_file: str = f"[blue]{location.is_file()}" if exists else "[blue italic]Unknown"
        is_dir: str = f"[blue]{location.is_dir()}" if exists else "[blue italic]Unknown"
        table.add_row(formatted_location, formatted_exists, is_file, is_dir)

    return table


@app.callback()
def root(verbose: bool = typer.Option(False, help="Enable verbose output.")) -> None:
    global is_verbose

    if verbose:
        is_verbose = True


@app.command()
def find(
    name: str = typer.Argument(..., help="The name of the entry."),
    database_location: Path = typer.Option(
        utils.config_folder(), help="The location of the database."
    ),
) -> None:
    """Find an entry with the name NAME"""
    database: Database = Database(database_location)
    _log(f"Got database, {database}")
    entry_: Optional[Entry] = _get_entry(name, database)
    if not database.exists():
        levels.info("Database doesn't exist, creating...")
        database.create()
    if not entry_:
        return
    table: Table = _gen_entry_table(entry_)
    return print(table)


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
