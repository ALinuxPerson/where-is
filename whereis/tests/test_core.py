from whereis import Database, Entry, exceptions
import pytest  # type: ignore
import os
from pathlib import Path
from typing import Dict, Union, List
import string
import random


def generate_random_string(max_chars: int = 8) -> str:
    return "".join([random.choice(string.ascii_letters) for _ in range(max_chars)])


def test_entry_attributes() -> None:
    entry: Entry = Entry("Test", ["{HOME}", "johndoe"], ["etc"])
    json_string: str = '{"name": "Test", "locations": [["{HOME}", "johndoe"], ["etc"]]}'
    entry_map: Dict[str, Union[str, List[List[str]]]] = {
        "name": "Test",
        "locations": [["{HOME}", "johndoe"], ["etc"]],
    }
    assert entry.name == "Test"
    assert entry.locations == [
        Path(os.path.join(os.path.sep, str(Path().home()), "johndoe")),
        Path(os.path.join(os.path.sep, "etc")),
    ]
    assert entry.to_dict == entry_map
    assert entry.to_json == json_string


def test_entry_equality() -> None:
    entry: Entry = Entry("Test", ["{HOME}", "johndoe"], ["etc"])
    other_equal_entry: Entry = Entry("Test", ["{HOME}", "johndoe"], ["etc"])
    other_inequal_entry: Entry = Entry("NotEqual", ["etc", "lib"])
    assert entry == other_equal_entry
    assert entry != other_inequal_entry


def test_entry_locations_exists() -> None:
    existing: str = generate_random_string()
    non_existing: str = generate_random_string()
    os.mknod(existing)
    entry: Entry = Entry("Test", ["{HOME}", existing], ["{HOME}", non_existing])
    for location, exists in entry.locations_exists().items():  # type: ignore
        assert location.exists() == exists

    os.remove(existing)


def test_database_attributes_and_context_manager_and_database_creation_and_deletion() -> None:
    location: Path = Path().home() / generate_random_string()
    with Database(location) as database:
        assert database.location == location
        assert database.location.exists()
        assert database.location.exists() == database.exists()
        assert database.entries
        for entry in database.entries:
            assert entry.name == "grub" or entry.name == "zsh"

    assert not location.exists()


def test_add_entry_to_database() -> None:
    entry: Entry = Entry("Test", ["{HOME}", "johndoe"], ["etc"])
    entry_: Entry = Entry("OtherTest", ["{HOME}", "bob"], ["lib"])
    location: Path = Path().home() / generate_random_string()
    with Database(location) as database:
        database.add(entry)
        assert entry in database.entries
        database += entry_
        assert entry_ in database.entries
        with pytest.raises(exceptions.EntryExistsError):
            database.add(entry)


def test_remove_entry_from_database() -> None:
    location: Path = Path().home() / generate_random_string()
    entry: Entry = Entry("Test", ["{HOME}", "johndoe"], ["etc"])
    with Database(location) as database:
        database += entry
        database.remove(entry)
        assert entry not in database.entries
        database += entry
        database -= entry
        assert entry not in database.entries
        with pytest.raises(exceptions.EntryNotFoundError):
            database.remove(entry)
