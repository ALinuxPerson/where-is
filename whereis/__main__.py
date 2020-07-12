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

    from whereis.clityper import main as cli_main

    return cli_main()


if __name__ == "__main__":
    main()
