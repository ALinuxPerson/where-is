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
from typing import Literal, Dict
from rich.console import Console
import sys

_console: Console = Console(file=sys.stderr)


def _levels(
    message: str,
    level: Literal["info", "success", "warn", "error"],
    no_icon: bool = False,
) -> None:
    """An easier way to get levels.

    Args:
        message: The message.
        level: The level.
        no_icon: Does the message have an icon or not?

    Returns:
        Nothing.
    """
    to_message: Dict[str, str] = {
        "info": " [dark_blue]{icon} [blue]{line}",
        "success": " [dark_green]{icon} [green4]{line}",
        "warn": " [yellow]{icon} [yellow3]{line}",
        "error": " [dark_red]{icon} [red]{line}",
    }
    icon: Dict[str, str] = {"info": "🛈", "success": "✓", "warn": "⚠", "error": "✗"}

    for line in message.splitlines():
        _console.print(
            to_message[level].format(
                icon="" if no_icon else f"[[{icon[level]}]]", line=line
            )
        )


def info(message: str, no_icon: bool = False) -> None:
    """Prints out an info message.

    Args:
        message: The message.
        no_icon: Does the message have an icon or not?

    Returns:
        Nothing.
    """
    return _levels(message, "info", no_icon)


def success(message: str, no_icon: bool = False) -> None:
    """Prints out a success message.

    Args:
        message: The message.
        no_icon: Does the message have an icon or not?

    Returns:
        Nothing.
    """
    return _levels(message, "success", no_icon)


def warn(message: str, no_icon: bool = False) -> None:
    """Prints out a warning message.

    Args:
        message: The message.
        no_icon: Does the message have an icon or not?

    Returns:
        Nothing.
    """
    return _levels(message, "warn", no_icon)


def error(message: str, no_icon: bool = False) -> None:
    """Prints out an error message.

    Args:
        message: The message.
        no_icon: Does the message have an icon or not?

    Returns:
        Nothing.
    """
    return _levels(message, "error", no_icon)


def debug(message: str) -> None:
    """Prints out a debug message.

    Args:
        message: The message.

    Returns:
        Nothing.
    """
    for line in message.splitlines():
        _console.log(f"[cyan]🔍 {line}")


def _test_levels() -> None:
    levels = [info, success, warn, error, debug]
    for level in levels:
        level("Hello, World!")  # type: ignore
        try:
            level("No icon!", no_icon=True)  # type: ignore
        except TypeError:
            pass


if __name__ == "__main__":
    _test_levels()
