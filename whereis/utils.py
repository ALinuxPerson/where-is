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
"""Some useful utilities to be used by where-is."""
from pathlib import Path
import platform
from typing import Dict
import os


def config_folder(system: str = platform.system()) -> Path:
    """Gets the config folder of each operating system.

    Args:
        system: The operating system to retrieve a config folder from.

    Returns:
        A path object that points to where a config folder is
        (if system is not in Linux, Mac, Windows it will default to Linux)
    """
    switch_case: Dict[str, Path] = {
        "Linux": Path().home() / ".config" / "where-is",
        "Mac": Path().home() / "Library" / "Preferences" / "where-is",
        "Windows": Path(
            str(os.getenv("APPDATA"))  # in case the os is other than windows
        )
        / "where-is",
    }

    return switch_case.get(system, switch_case["Linux"])
