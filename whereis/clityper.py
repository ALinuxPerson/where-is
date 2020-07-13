import typer
from pathlib import Path
from whereis import utils, levels, Database, Entry, input, version
from typing import Optional, List
from rich.table import Table
from rich import print
from rich.console import Console

app: typer.Typer = typer.Typer(
    help="An elegant way to find configuration files (and folders)."
)
is_verbose: bool = False
VERSION_STRING: str = f"""[bold dark_blue]  ---       [/][italic]where-is[/] {version} Copyright (C) 2020
[bold dark_blue] /          [/]Made by [italic bold]ALinuxPerson[/].
[bold dark_blue]<  ?
 \\          [/][italic]This program comes with [bold]ABSOLUTELY NO WARRANTY[/]; This is free software,
[bold dark_blue]  ---       [/]and you are welcome to redistribute it under certain conditions."""


def _log(message: str) -> None:
    return levels.debug(message) if is_verbose else None


def _get_entry(
    entry_name: str, database: Database, no_err: bool = False
) -> Optional[Entry]:
    for entry_ in database.entries:
        _log(f"Checking if [bold]'{entry_.name}'[/] == [bold]'{entry_name}'[/]...")
        if entry_.name == entry_name:
            _log(f"Got entry, {entry_}")
            return entry_
    else:
        if not no_err:
            levels.error(f"Couldn't find entry '{entry_name}' in the database.")
        else:
            _log(
                f"Couldn't find any entry, but the no_err argument is True, so not printing any errors."
            )
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


def _eval_db_opts(info: bool, add: bool, remove: bool) -> bool:
    _log(f"Got options:\n" f"info: {info}, add: {add}, remove: {remove}")
    if info and add or info and remove:
        levels.error(
            f"The info option is mutually exclusive with the add and remove options."
        )
        return False
    elif add and remove:
        levels.error("The add and remove options are mutually exclusive.")
        return False
    else:
        return True


def _get_database(location: Path) -> Database:
    database: Database = Database(location)
    _log(f"Got database, {database}")
    if not database.exists():
        levels.info("Database doesn't exist, creating...")
        database.create()

    return database


def _add_entry(database: Database) -> bool:
    levels.info("Enter the name of the entry.")
    entry_name: str = input("[blue]Entry name: ")
    if entry_name in [entry.name for entry in database.entries]:
        levels.error("That entry already exists.")
        return False
    entry_locations: List[str] = []
    levels.info("Enter locations for the entry. Press ctrl-C to finish.")
    while True:
        try:
            entry_location: str = input("[blue]Entry locations: ")
            entry_locations.append(entry_location)
        except KeyboardInterrupt:
            break
    entry: Entry = Entry(entry_name, *entry_locations)  # type: ignore
    database += entry  # type: ignore
    print("Added entry to database.")
    return True


def _rm_entry(database: Database) -> None:
    levels.info("Enter the name of the entry: ")
    entry: Optional[Entry] = _get_entry(input("[blue]Entry name: "), database)
    if not entry:
        return
    database -= entry  # type: ignore
    levels.success("Removed entry from the database.")


def _show_version(value: bool) -> None:
    if value:
        console: Console = Console()
        console.print(VERSION_STRING, style="blue")
        raise typer.Exit()


# noinspection PyUnusedLocal
@app.callback()
def root(
    verbose: bool = typer.Option(False, help="Enable verbose output."),
    version_: bool = typer.Option(
        None,
        "--version",
        help="Show this program's version number and credits",
        callback=_show_version,
    ),
) -> None:
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
    database: Database = _get_database(database_location)
    entry_: Optional[Entry] = _get_entry(name, database)
    if not entry_:
        return
    table: Table = _gen_entry_table(entry_)
    return print(table)


@app.command("database")
def cli_database(
    location: Path = typer.Option(
        utils.config_folder(), help="The location of the database."
    ),
    info: bool = typer.Option(
        False, "--info", help="Show information about the entry."
    ),
    add: bool = typer.Option(False, "--add", help="Add the entry to the database."),
    remove: bool = typer.Option(
        False, "--remove", help="Remove the entry from the database."
    ),
) -> None:
    """Query, add and remove the entry with the name NAME."""
    database: Database = _get_database(location)
    if not _eval_db_opts(info, add, remove):
        return
    if info:
        return print(database)
    elif add:
        _add_entry(database)
    elif remove:
        _rm_entry(database)
    else:
        levels.info("What do you want to do? pass the '--help' argument to get help.")


def main() -> None:
    return app()
