"""The main entry point for pip and `python -m`."""
from typing import List
import sys


def process_imports(package_name: str) -> bool:
    """Processes imports to determine if they're installed or not.

    Args:
        package_name: The package name.

    Returns:
        True if the package is installed, else False.
    """
    try:
        __import__(package_name)
        return True
    except ImportError:
        print(
            f" [✗] The package {package_name} isn't installed on your system.",
            file=sys.stderr,
        )
        return False


def main() -> None:
    """Main entry point.

    Returns:
        Nothing.
    """
    to_import: List[str] = ["rich", "typer"]
    if False in (process_imports(package_name) for package_name in to_import):
        sys.exit(2)

    from whereis.cli import main as cli_main

    return cli_main()


if __name__ == "__main__":
    main()
