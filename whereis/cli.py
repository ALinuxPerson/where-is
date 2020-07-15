"""The cli frontend for where-is."""
import typer
from pathlib import Path
from whereis import utils, levels, Database, Entry, input, version, exceptions
from typing import Optional, List
from rich import print
from rich.console import Console

app: typer.Typer = typer.Typer(
    help="An elegant way to find configuration files (and folders)."
)
is_verbose: bool = False
database_location: Path = utils.config_folder()
VERSION_STRING: str = f"""[bold dark_blue]  ---       [/][italic]where-is[/] {version} Copyright (C) 2020
[bold dark_blue] /          [/]Made by [italic bold]ALinuxPerson[/]. This project uses the [italic bold]GNU GPLv3[/] license.
[bold dark_blue]<  ?
 \\          [/][italic]This program comes with [bold]ABSOLUTELY NO WARRANTY[/]; This is free software,
[bold dark_blue]  ---       [/]and you are welcome to redistribute it under certain conditions."""


def _log(message: str) -> None:
    return levels.debug(message) if is_verbose else None


def _get_entry(
    entry_name: str, database: Database, no_err: bool = False
) -> Optional[Entry]:
    """Gets an entry safely.

    This function prevents exceptions from being printed out from core and instead replaces them with not so verbose,
    user friendly messages.

    Args:
        entry_name: The entry name.
        database: The database.
        no_err: Should no errors be displayed?

    Returns:
        An entry if no error was encountered, else nothing.
    """
    for entry_ in database.entries:
        _log(f"Checking if [bold]'{entry_.name}'[/] == [bold]'{entry_name}'[/]...")
        try:
            if entry_.name == entry_name:
                _log(f"Got entry, {entry_}")
                return entry_
        except exceptions.FormatMapError as error:
            levels.error(f"Entry formatting error: [italic]{error.message}")
            return None
    else:
        if not no_err:
            levels.error(f"Couldn't find entry '{entry_name}' in the database.")
        else:
            _log(
                f"Couldn't find any entry, but the no_err argument is True, so not printing any errors."
            )
        return None


def _eval_db_opts(info: bool, add: bool, remove: bool, delete: bool) -> bool:
    """Evaluates the options given by the user in the `where-is database [OPTIONS]` argument.

    The `where-is database [OPTIONS]` arguments are all mutually exclusive, which means this needs to be implemented to
    enforce that mutually-exclusiveness.

    Args:
        info: The info option.
        add: The add option.
        remove: The remove option.
        delete: The delete option.

    Returns:
        True if the options are mutually exclusive, else False.
    """
    _log(
        f"Got options:\n"
        f"info: {info}, add: {add}, remove: {remove}, delete: {delete}"
    )
    opts: List[bool] = [info, add, remove, delete]
    if opts.count(True) > 1:
        levels.error(
            f"The info, add, remove and delete options are mutually exclusive with each other."
        )
        return False
    return True


def _get_database(location: Path) -> Optional[Database]:
    """Gets a database object safely.

    This function prevents exceptions from being printed out from core and instead replaces them with not so verbose,
    user friendly messages. If the database doesn't exist, this function creates it automatically.

    Args:
        location: The location where the database is.

    Returns:
        A database object if no error was encountered, else nothing.
    """
    database: Database = Database(location)
    if not database.exists():
        try:
            levels.info("Database doesn't exist, creating...")
            database.create()
        except PermissionError as error:
            levels.error(
                f"Can't create database at location '{location}': [italic]{error}"
            )
            return None
    try:
        _: List[Entry] = database.entries
    except exceptions.EntryParseError as error:
        levels.error(f"Database error: [italic]{error.message}")
        return None
    _log(f"Got database, {database}")

    return database


def _add_entry(database: Database) -> bool:
    """Adds an entry safely.

    This function helps the user to add an entry to a database.

    Args:
        database: The database object.

    Returns:
        True if no error was encountered, else False.
    """
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
    entry: Entry = Entry(entry_name, *[Path(entry_).parts for entry_ in entry_locations])  # type: ignore
    database += entry  # type: ignore
    levels.success("Added entry to database.")
    return True


def _rm_entry(database: Database) -> None:
    """Removes an entry safely.

    This function prevents exceptions from being printed out from core and instead replaces them with not so verbose,
    user friendly messages.

    Args:
        database: The database object.

    Returns:
        Nothing.
    """
    levels.info("Enter the name of the entry: ")
    entry: Optional[Entry] = _get_entry(input("[blue]Entry name: "), database)
    if not entry:
        return
    database -= entry  # type: ignore
    levels.success("Removed entry from the database.")


def _del_db(database: Database) -> None:
    """Deletes a database safely.

    This function prevents exceptions from being printed out from core and instead replaces them with not so verbose,
    user friendly messages.

    Args:
        database: The database object.

    Returns:
        Nothing.
    """
    try:
        database.delete()
        levels.success("Successfully deleted database.")
    except exceptions.DatabaseNotFoundError as error:
        levels.error(f"Error: [italic]{error}")


def _show_version(value: bool) -> None:
    """Shows the formatted version.

    Args:
        value: Required otherwise _show_version always gets executed.

    Returns:
        Nothing.
    """
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
    database_location_: Path = typer.Option(
        None, "--database-location", help="Specify the database location."
    ),
) -> None:
    """The root arguments.

    Args:
        verbose: Enable verbose output.
        version_: Show version.
        database_location_: Specify the database location.

    Returns:
        Nothing.
    """
    global is_verbose
    global database_location

    if verbose:
        is_verbose = True

    if database_location_:
        database_location = database_location_


@app.command()
def find(name: str = typer.Argument(..., help="The name of the entry.")) -> None:
    """Find an entry with the name NAME"""
    database: Optional[Database] = _get_database(database_location)
    if not database:
        return
    entry_: Optional[Entry] = _get_entry(name, database)
    if not entry_:
        return
    print(entry_)


@app.command("database")
def cli_database(
    info: bool = typer.Option(False, "--info", help="Show information about an entry."),
    add: bool = typer.Option(False, "--add", help="Add an entry to a database."),
    remove: bool = typer.Option(
        False, "--remove", help="Remove an entry from a database."
    ),
    delete: bool = typer.Option(False, "--delete", help="Deletes the database."),
) -> None:
    """Query, add and remove entries from the database and perform operations on the database itself."""
    database: Optional[Database] = _get_database(
        database_location
    ) if not delete else Database(database_location)
    if not _eval_db_opts(info, add, remove, delete) or not database:
        return
    if info:
        try:
            return print(database)
        except exceptions.FormatMapError as error:
            levels.error(
                f"Unable to create table:\n" f"Entry formatting error: [italic]{error}"
            )
    elif add:
        _add_entry(database)
    elif remove:
        _rm_entry(database)
    elif delete:
        _del_db(database)
    else:
        levels.info(
            "What do you want to do? pass the [bold]'--help'[/] argument to get help."
        )


def main() -> None:
    """The main entry point.

    Returns:
        Nothing.
    """
    return app()
