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


class WhereIsException(Exception):
    """Base class for all where-is related exceptions."""

    @property
    def message(self) -> str:
        """Gets error message.

        Returns:
            The error message.
        """
        return self.args[0]

    @property
    def name(self) -> str:
        """Gets the error name.

        Returns:
            The error name.
        """
        return self.__class__.__name__


class EntryExistsError(WhereIsException):
    """Raised when a database entry exists."""


class EntryDoesNotExistError(WhereIsException):
    """Raised when a database entry doesn't exist."""
