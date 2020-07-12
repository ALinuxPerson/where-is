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
import json
from typing import List, Dict, Union
from pathlib import Path
import os
from whereis import exceptions, utils
import shutil
from rich.table import Table


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
            Path(self._format_path(os.path.join(os.path.sep, *location)))
            for location in self._locations
        ]

    @property
    def to_dict(self) -> Dict[str, Union[str, List[List[str]]]]:
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
        return json.dumps(self.to_dict)

    @staticmethod
    def _format_path(path: str) -> str:
        """Formats a path.

        Args:
            path: The path to format.

        Returns:
            The formatted path.
        """
        format_map: Dict[str, str] = {
            "HOME": str(Path().home()),
            "WHEREIS_CONFIG": str(utils.config_folder()),
            "CONFIG_FOLDER": str(utils.config_folder().parent),
        }
        try:
            return path.format(**format_map)
        except (KeyError, IndexError, ValueError):
            raise KeyError(f"Format map not supported for path '{path}'.") from None

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
        """
        ret: List[Dict[str, Union[str, List[List[str]]]]] = []
        for entry in self.location.iterdir():
            if entry.suffix == ".json":
                try:
                    ret.append(json.loads(entry.read_text()))
                except json.decoder.JSONDecodeError as error:
                    raise ValueError(
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
            KeyError: If the raw entry doesn't follow the json schema.
        """
        try:
            return Entry(raw_entry["name"], *raw_entry["locations"])  # type: ignore
        except KeyError:
            raise ValueError(f"JSON schema incorrect: {raw_entry}") from None

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
            raise exceptions.EntryDoesNotExistError("The database entry must exist.")
        entry_to_delete: Path = self.location / f"{entry.name}.json"
        entry_to_delete.unlink()

    def create(self) -> None:
        """Creates the database if it doesn't exist.

        Returns:
            Nothing.
        """
        if self.exists():
            raise FileExistsError("The database already exists!")
        sample_db: Path = Path(__file__).parent / "database"
        Path(self.location).mkdir()
        for path in sample_db.iterdir():
            shutil.copyfile(str(path), str(self.location / path.name))

    def exists(self) -> bool:
        """Check if the database exists.

        Returns:
            True if the folder contacting the database exists, else False
        """
        return self.location.exists()

    def __rich__(self) -> Table:
        table: Table = Table(title="Database Info")
        table.add_column("Info")
        table.add_column("Answer")
        map_: Dict[str, str] = {
            "Location": str(self.location),
            "Entries": "\n".join(str(entry) for entry in self.entries),
            "Exists": utils.format_bool(self.exists()),
        }
        for info, answer in map_.items():
            table.add_row(info, answer)

        return table

    def __add__(self, other: Entry) -> None:
        return self.add(other)

    def __sub__(self, other: Entry) -> None:
        return self.remove(other)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} object: location={self.location}>"
