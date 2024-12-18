"""Exceptions module which contains Exception classes, which are raised by
raised by methods/functions used by the Typer CLI

Classes:
    CompilationError: Raised when mpy-cross fails to compile a file.
    StandardLibraryError: Raised when installing packages already in standard
        library.
"""

import pathlib


class CompilationError(Exception):
    """Raised when mpy-cross fails to compile a python file."""

    def __init__(self, path: pathlib.Path):
        """Initialise Exception.

        Args:
            path (Path): Path of compilation target.
        """

        self.path = path

    def __str__(self) -> str:
        """Format Exception string representation."""

        return f"Compilation error ({self.path})"


class StandardLibraryError(Exception):
    """Raised when installing packages already in standard library."""

    def __init__(self, message: str):
        """Initialise Exception.

        Args:
            message (str): Exception message.
        """

        super().__init__(message)

    def __str__(self) -> str:
        """Format Exception string representation."""

        return f"Attempted standard library install ({self.message})."
