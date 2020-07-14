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
