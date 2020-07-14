"""Exceptions used by where-is."""


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


class EntryNotFoundError(WhereIsException):
    """Raised when a database entry doesn't exist."""


class FormatMapError(WhereIsException):
    """Raised when a format map is invalid."""


class EntryParseError(WhereIsException):
    """Raised when an error is encountered during parsing of a json entry."""


class DatabaseExistsError(WhereIsException):
    """Raised when a database exists."""


class DatabaseNotFoundError(WhereIsException):
    """Raised when a database isn't found."""
