"""Project directory module containing classes and functions used to
establish main project working directories.

Author: Andrew Ridyard.
License: GNU General Public License v3 or later.
Copyright (C): 2024.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Classes:
    ProjectPath: Stores references to project directories.
"""

import functools
import itertools
import operator
import pathlib
from typing import Iterable, Iterator, Union


class ProjectPath:
    """Class providing properties for project directories."""

    def __init__(self):
        """Initialise class by identifying project root directory. All
        other directories are inferred from project root.

        Raises:
            FileExistsError if project root not identified.
        """

        marker_exists = operator.methodcaller("is_file")

        # marker files indicative of project root
        markers = ("pyproject.toml", "README.md", "LICENSE")

        current_directory = pathlib.Path.cwd().resolve()
        for path in (current_directory, *current_directory.parents):
            if marker_exists(path / ".picoproject"):
                self._root = path
                break

            marker_paths = zip(itertools.repeat(path, len(markers)), markers)
            if any(map(marker_exists, self._combine_paths(marker_paths))):
                self._root = path
                break

        if not hasattr(self, "_root"):
            message = f"Root directory not identified - missing {markers}."
            raise FileExistsError(message)

        package_name = self._root.name.lower().replace("-", "_")
        if (self._root / "src" / package_name).is_dir():
            self._package = self._root / "src" / package_name
        elif (self._root / package_name).is_dir():
            self._package = self._root / package_name

        self._lib = self._package / "lib"
        self._certs = self._package / "certs"
        self._env = self._package / "env"
        self._server = self._package / "server"
        self._export = self._root / "export"

    @property
    def root(self) -> pathlib.Path:
        """Root directory Path instance."""
        return self._root

    @functools.cached_property
    def package(self) -> pathlib.Path:
        """Package directory Path instance."""
        return self._package

    @property
    def lib(self) -> pathlib.Path:
        """Package lib directory Path instance."""
        return self._lib

    @property
    def certs(self) -> pathlib.Path:
        """Package certs directory Path instance."""
        return self._certs

    @property
    def env(self) -> pathlib.Path:
        """Package env directory Path instance."""
        return self._env

    @property
    def server(self) -> pathlib.Path:
        """Package server directory Path instance."""
        return self._server

    @property
    def export(self) -> pathlib.Path:
        """Package export directory Path instance."""

        return self._export

    @export.setter
    def export(self, name: str) -> pathlib.Path:
        """Setter method for export property."""

        self._export = self.package / name

    @property
    def python(self) -> tuple[pathlib.Path]:
        """Python file path instances within package."""
        return tuple(
            itertools.chain(self.package.glob("*.py"), self.lib.rglob("*.py"))
        )

    @staticmethod
    def _combine_paths(
        items: Iterator[Iterable[Union[str, pathlib.Path]]],
    ) -> Iterator:
        """Combine two Path instances or a Path and a str to make a new Path.

        Args:
            path_items (PathItems): Path items to combine

        Returns:
            Combined Path from object pairs
        """
        return itertools.starmap(operator.truediv, items)
