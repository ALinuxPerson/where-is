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
from whereis.database import *
from whereis import levels
from rich.traceback import Traceback, TracebackType
from rich.console import Console
from typing import Type
import sys


def excepthook(
    type_: Type[BaseException], value: BaseException, traceback: TracebackType,
) -> None:
    levels.error(f"[bold]Exception[/] occurred, please wait for it to be processed...")
    traceback_console: Console = Console(file=sys.stderr)

    traceback_console.print(
        Traceback.from_exception(
            type_,
            value,
            traceback,
            width=100,
            extra_lines=3,
            theme=None,
            word_wrap=False,
        )
    )
    levels.error(
        f"Please report this exception here: [blue underline]https://github.com/what-to-code-complete/where-is/issues"
    )
    levels.info(
        "[bold]Post-mortem information[/]\n"
        "[underline]How to report this exception:[/]\n"
        "[italic]1. Capture stdout and stderr to file:\n"
        "\t$ <YOUR_ERRORED_CMD> >> error.log 2>&1\n"
        "[italic]2. Upload 'error.log' as a gist [bold](note: only gists are allowed.)[/]\n"
        "[italic]3. Attach it to your issue [bold](give your issue a descriptive title and description!)[/]"
    )


sys.excepthook = excepthook
