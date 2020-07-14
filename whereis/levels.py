"""Custom messages."""
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
        "info": " [bold][dark_blue]{icon} [blue]{line}",
        "success": " [bold][dark_green]{icon} [green4]{line}",
        "warn": " [bold][yellow]{icon} [yellow3]{line}",
        "error": " [bold][dark_red]{icon} [red]{line}",
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
    """Tests levels.

    Returns:
        Nothing.
    """
    levels = [info, success, warn, error, debug]
    for level in levels:
        level("Hello, World!")  # type: ignore
        try:
            level("No icon!", no_icon=True)  # type: ignore
        except TypeError:
            pass


if __name__ == "__main__":
    _test_levels()
