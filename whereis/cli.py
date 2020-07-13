# where-is: Finds config files.
# Copyright (C) 2020 ALinuxPerson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from whereis import Database, Entry, levels, utils
from rich.table import Table
from rich.console import Console
from pathlib import Path
import fire  # type: ignore
from rich import print
import subprocess
from typing import Dict, Union, List, Optional
import tempfile
import json


def _get_version() -> str:
    return (Path(__file__).parent.parent / "VERSION").read_text().strip()


VERSION_STRING: str = f"""[bold green4]  ---       [/]where-is {_get_version()} Copyright (C) 2020
[bold green4] /          [/]Made by [underline]ALinuxPerson[/].
[bold green4]<  ?
 \\          [/][italic]This program comes with [bold]ABSOLUTELY NO WARRANTY[/]; This is free software,
[bold green4]  ---       [/]and you are welcome to redistribute it under certain conditions."""


def new_entry(
    name: str,
    database_location: str,
    text_editor: Optional[str] = utils.get_text_editor(),
) -> None:
    if not text_editor:
        levels.error(f"Couldn't find any text editor in the system.")
        return

    temp: Dict[str, Union[str, List[List[str]]]] = {
        "_comment": "Format map for locations: \n"
        "{HOME}: Your home folder.\n"
        "{WHEREIS_CONFIG}: The where-is configuration folder.\n"
        "{CONFIG_FOLDER}: The configuration folder.",
        "name": name,
        "locations": [["ENTER HERE"]],
    }
    temp_path: Path = Path(
        tempfile.gettempdir()
    ) / f"where-is-{utils.generate_string()}.tmp"

    with temp_path.open("w") as tmp:
        tmp.write(json.dumps(temp))

    called = utils.sp_call(f"{utils.get_text_editor()} {temp_path.absolute()}")

    if called.return_code != 0:
        levels.error(
            f"Process gave non-zero exit code (failure).\n"
            f"stdout:\n"
            f"{called.stdout or '(nothing)'}\n\n"
            f"stderr:\n"
            f"{called.stderr or '(nothing)'}"
        )
        return

    levels.info("Moving entry to database...")
    temp_path.replace(Path(database_location) / f"{name}.json")


def _check_for_db_entries(database: Database) -> bool:
    if not database.entries:
        levels.error("Couldn't find any entries in the database.")
        return False
    else:
        return True


def find(name: str, database_location: str = str(utils.config_folder())) -> None:
    while True:
        try:
            database_location: Path = Path(database_location)  # type: ignore
            database: Database = Database(database_location)  # type: ignore
            try:
                if not _check_for_db_entries(database):
                    return
            except ValueError as error:
                levels.error(f"Parse failure: {error}")
                return
            break
        except TypeError:
            levels.error(
                "You aren't supposed to pass '--database-location' like a flag."
            )
            return
        except NotADirectoryError:
            if database_location.exists():  # type: ignore
                levels.error(
                    "The database location exists and is a file. Either,\n"
                    "a.) Remove that file then try again, or\n"
                    "b.) Choose another database location by passing '--database-location <DB_LOCATION>'."
                )
                return
            else:
                levels.info("Database doesn't exist, creating.")
                # noinspection PyUnboundLocalVariable
                database.create()
    table: Table = Table(title="[bold]Config files found")
    table.add_column("Locations")
    table.add_column("Exists")
    table.add_column("Is a file?")
    while True:
        try:
            entry: Entry = next(
                iter([entry for entry in database.entries if entry.name == name])
            )
            break
        except StopIteration:
            levels.error(f"Couldn't find the entry '{name}'.")
            return
        except NotADirectoryError:
            levels.info("Database doesn't exist, creating.")
            database.create()
            continue
    try:
        # noinspection PyUnboundLocalVariable
        for location, exists in entry.locations_exists().items():
            table.add_row(
                f"[green4 bold]{location}",
                f"[green4 bold]{exists}" if exists else f"[red bold]{exists}",
                f"[blue]{location.is_file()}" if exists else "[blue italic]Unknown",
            )
    except KeyError as error:
        levels.error(
            f"Couldn't parse path:\n"
            f"[bold]{error.__class__.__name__}:[/] [italic]{error}"
        )
        return

    print(table)


def show_version() -> None:
    console: Console = Console()
    console.print(VERSION_STRING, style="blue")


def cli(
    name: str = None,
    database_location: str = None,
    version: bool = False,
    new: bool = False,
) -> None:
    """Finds configuration files.

    Args:
        name: The name of the entry to search for.
        database_location: The database to search for the entry. Defaults to the where-is config folder.
        version: Show this program's version number and credits then exit.
        new: Create a new entry with the name argument.

    Returns:
        Nothing.
    """
    if version:
        return show_version()
    else:
        if not name:
            if database_location:
                levels.error("You need to pass the '-n' or '--name' argument first!")
            else:
                levels.info(
                    "What do you want to do? Pass the '-h' or '--help' argument to get more info."
                )
            return
        if new:
            return new_entry(name, database_location or str(utils.config_folder()))
        find(name, database_location or str(utils.config_folder()))


def main() -> None:
    fire.Fire(cli)
