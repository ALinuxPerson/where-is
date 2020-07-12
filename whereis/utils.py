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
from pathlib import Path
import platform
from typing import Dict, Optional, List, NamedTuple, Type
import os
import random
import string
import shutil
import subprocess


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


def generate_string(num_range: int = 8) -> str:
    """Generates a random string.

    Args:
        num_range: The range to generate characters.

    Returns:
        A random string.
    """
    return "".join(random.choice(string.ascii_letters) for _ in range(num_range))


def get_text_editor() -> Optional[str]:
    to_find: List[str] = [
        os.getenv("EDITOR", ""),
        "micro",
        "nano",
        "vim",
        "emacs",
        "vi",
        "subl",
        "vscode",
        "kate",
        "geany",
        "gedit",
        "notepad++.exe",
        "notepad.exe",
        "ed",
    ]
    for program in to_find:
        found: Optional[str] = shutil.which(program)
        if not found:
            continue
        else:
            return found
    else:
        return None


def bytes_to_string(bytes_obj: bytes, encoding: str = "utf-8") -> str:
    return bytes_obj.decode(encoding)


def sp_call(command: str):
    out = NamedTuple("Output", [("stdout", str), ("stderr", str), ("return_code", int)])
    process: subprocess.Popen = subprocess.Popen(
        command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    process.wait()  # wait for process to return an exit code
    stdout, stderr = process.communicate()
    return out(bytes_to_string(stdout), bytes_to_string(stderr), process.returncode)


def format_bool(boolean: bool) -> str:
    return f"[green4 italic]{boolean}" if boolean else f"[red italic]{boolean}"
