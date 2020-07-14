"""The core of where-is. This is where the CLI frontend gets its objects from."""
import json
from typing import List, Dict, Union
from pathlib import Path
import os
from whereis import exceptions, utils
import shutil
from rich.table import Table
from rich.tabulate import tabulate_mapping


class Entry:
    def __init__(self, name: str, *locations: List[str]) -> None:
        """Initializes an Entry object.

        Args:
            name: The name of an entry.
            *locations: The locations the entry stores.
        """
        self._name = name
        self._locations = locations

    @property
    def name(self) -> str:
        """The name of the entry.

        Returns:
            The name of the entry
        """
        return self._name

    @property
    def locations(self) -> List[Path]:
        """All of the locations an entry has.

        Notes:
            The paths can be formatted.
            Here is the following format map:
                {HOME}: Your home folder.
                {WHEREIS_CONFIG}: The where-is configuration folder.
                {CONFIG_FOLDER}: The configuration folder.

        Returns:
            All of the locations an entry has.
        """
        return [
            Path(self._format_path(Path(os.path.join(os.path.sep, *location))))
            for location in self._locations
        ]

    @property
    def _to_dict(self) -> Dict[str, Union[str, List[List[str]]]]:
        """Converts a entry object to a dictionary.

        Returns:
            Converted to dictionary entry object.
        """
        return {
            "name": self.name,
            "locations": self._locations,  # type: ignore
        }

    @property
    def to_json(self) -> str:
        """Converts an entry object to json.

        Returns:
            Converted to json entry object.
        """
        return json.dumps(self._to_dict)

    @staticmethod
    def _format_path(path: Path) -> Path:
        """Formats a path.

        Args:
            path: The path to format.

        Returns:
            The formatted path.
        """
        format_map: Dict[str, Path] = {
            "HOME": Path().home(),
            "WHEREIS_CONFIG": utils.config_folder(),
            "CONFIG_FOLDER": utils.config_folder().parent,
        }
        try:
            path_parts: List[str] = list(path.parts)
            for index, part in enumerate(path_parts):
                for name, value in format_map.items():
                    if name in part:
                        del path_parts[index]
                        path_parts[index:index] = list(value.parts)

            return Path(*path_parts)
        except (KeyError, IndexError, ValueError):
            raise exceptions.FormatMapError(
                f"Format map not supported for path '{path}'."
            ) from None

    def locations_exists(self) -> Dict[Path, bool]:
        """Does each location exist?

        Returns:
            A dictionary of locations and whether that location exists.
        """
        return {location: location.exists() for location in self.locations}

    def __eq__(self, other) -> bool:
        try:
            return self.name == other.name and self.locations == other.locations
        except AttributeError:
            return False

    def __rich__(self) -> Table:
        """A shortcut to generate a table to generate configuration files found.

        Returns:
            A table object, usable by rich print instances.
        """
        columns: List[str] = ["Locations", "Exists", "Is File", "Is Folder"]
        table: Table = Table(title="[bold purple]Config files found")
        for column in columns:
            table.add_column(column)
        for location, exists in self.locations_exists().items():
            formatted_location: str = f"[magenta]{location}"
            formatted_exists: str = f"[red]{exists}" if not exists else f"[green4]{exists}"

            if exists and location.is_file():
                is_file: str = "[green4]True"
            elif exists and not location.is_file():
                is_file = "[red]False"
            else:
                is_file = "[red italic]Unknown"

            if exists and location.is_dir():
                is_dir: str = "[green]True"
            elif exists and not location.is_dir():
                is_dir = "[red]False"
            else:
                is_dir = "[red italic]Unknown"

            table.add_row(formatted_location, formatted_exists, is_file, is_dir)

        return table

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} object: name='{self.name}' locations={self.locations}>"


class Database:
    def __init__(self, location: Path = utils.config_folder()) -> None:
        """Initializes a Database object.

        Args:
            location: The location where the database is. Defaults to the config folder.
        """
        self._location = location

    @property
    def location(self) -> Path:
        """The location where the database is.

        Returns:
            The location where the database is.

        Raises:
            NotADirectoryError: When the database folder doesn't exist.
        """
        return self._location

    @property
    def _database(self) -> List[Dict[str, Union[str, List[List[str]]]]]:
        """All of the database entries in raw, waiting to be processed.

        Returns:
            A list of dictionaries if the file owning that dictionary's suffix is '.json'.

        Raises:
            EntryParseError: If the entry JSON can't be decoded.
        """
        ret: List[Dict[str, Union[str, List[List[str]]]]] = []
        for entry in self.location.iterdir():
            if entry.suffix == ".json":
                try:
                    ret.append(json.loads(entry.read_text()))
                except json.decoder.JSONDecodeError as error:
                    raise exceptions.EntryParseError(
                        f"Error parsing '{entry.absolute()}': {error}"
                    ) from None

        return ret

    @staticmethod
    def _entry_from_json(raw_entry: Dict[str, Union[str, List[List[str]]]]) -> Entry:
        """Converts a json dict to an Entry object.

        Args:
            raw_entry: The entry in json dict.

        Returns:
            An entry object.

        Raises:
            EntryParseError: If the raw entry doesn't follow the json schema.
        """
        try:
            return Entry(raw_entry["name"], *raw_entry["locations"])  # type: ignore
        except KeyError:
            raise exceptions.EntryParseError(
                f"JSON schema incorrect: {raw_entry}"
            ) from None

    @property
    def entries(self) -> List[Entry]:
        """A list of all entries.

        Returns:
            A list of entry objects from the database location.
        """
        return [self._entry_from_json(raw_entry) for raw_entry in self._database]

    def add(self, entry: Entry) -> None:
        """Adds an entry to the database.

        Args:
            entry: The entry object.

        Returns:
            Nothing.

        Raises:
            EntryExistsError: If the entry object exists in the database entries.
        """
        if entry in self.entries:
            raise exceptions.EntryExistsError("The database entry exists.")
        new_entry: Path = self.location / f"{entry.name}.json"
        new_entry.write_text(entry.to_json)

    def remove(self, entry: Entry) -> None:
        """Removes an entry from the database.

        Args:
            entry: The entry object.

        Returns:
            Nothing.

        Raises:
            EntryDoesNotExistError: If the entry object doesn't exist in the database entries.
        """
        if entry not in self.entries:
            raise exceptions.EntryNotFoundError("The database entry must exist.")
        entry_to_delete: Path = self.location / f"{entry.name}.json"
        entry_to_delete.unlink()

    def create(self) -> None:
        """Creates the database if it doesn't exist.

        Returns:
            Nothing.

        Raises:
            DatabaseExistsError: If the database exists.
        """
        if self.exists():
            raise exceptions.DatabaseExistsError("The database already exists!")
        sample_db: Path = Path(__file__).parent / "database"
        Path(self.location).mkdir()
        for path in sample_db.iterdir():
            shutil.copyfile(str(path), str(self.location / path.name))

    def delete(self) -> None:
        """Deletes the database if it exists.

        Notes:
            There is no way to implement a python native shortcut for this because __del__ gets called after program
            exit, which means the database will get deleted after program exit.

        Returns:
            Nothing.

        Raises:
            DatabaseNotFoundError: If the database doesn't exist.
        """
        if not self.location.exists():
            raise exceptions.DatabaseNotFoundError("The database doesn't exist!")
        return shutil.rmtree(self.location)

    def exists(self) -> bool:
        """Check if the database exists.

        Returns:
            True if the folder contacting the database exists, else False
        """
        return self.location.exists()

    def __rich__(self) -> Table:
        """A shortcut to generate database info.

        Returns:
            A table, usable by rich print instances.
        """
        map_: Dict[str, Union[Path, List[Entry], bool]] = {
            "Location": self.location,
            "Entries": self.entries,
            "Exists": self.exists(),
        }
        table: Table = tabulate_mapping(map_, title="Database Info")

        return table

    def __add__(self, other: Entry) -> None:
        """A python native shortcut of database.add().

        Args:
            other: The other class (should be an Entry object)

        Returns:
            Nothing.
        """
        return self.add(other)

    def __sub__(self, other: Entry) -> None:
        """A python native shortcut of database.remove().

        Args:
            other: The other class (should be an Entry object)

        Returns:
            Nothing.
        """
        return self.remove(other)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} object: location={self.location}>"
