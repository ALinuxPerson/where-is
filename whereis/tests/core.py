from whereis import Database, Entry
import pytest
import os
from pathlib import Path
from typing import Dict, Union, List


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
