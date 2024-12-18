"""Installation helper functions and classes for Typer CLI.

Classes:
    PackageIndex: Used to interface with the Micropython index.

Functions:
    download_mpy_package: Downloads packages from MicroPython index.
"""

import functools
import json
import operator
import pathlib
import traceback
import urllib.request
from urllib.error import URLError


class PackageIndex:
    """Class to store MicroPython package index details."""

    index_url = "https://micropython.org/pi/v2/index.json"

    def __init__(self):
        """Initialise PackageIndex."""

        with urllib.request.urlopen(self.index_url) as r:
            package_index = json.loads(r.read())
        self._index = tuple(package_index["packages"])

    @property
    def index(self) -> tuple[dict, ...]:
        """MicroPython package index.

        Returns:
            tuple containing package information dicts
        """
        return self._index

    @functools.cached_property
    def standard_library(self) -> tuple:
        """Reference to all standard library package names.

        Returns:
            tuple containing standard library package names.
        """
        packages = filter(self._filter_stdlib, self.index)
        return tuple(map(operator.itemgetter("name"), packages))

    @staticmethod
    def _filter_stdlib(package_info: dict) -> bool:
        """MicroPython standard library filter method.

        Args:
            package_info (dict): MicroPython package information.

        Returns:
            True if package is in standard library else False.
        """
        return package_info.get("path", "").startswith("python-stdlib")


def download_mpy_package(package: str, target: pathlib.Path):
    """Downloads a MicroPython package and dependencies, saving all
    files to the 'project-slug/src/project_name/lib directory'.

    NOTE: MicroPython index is @ https://micropython.org/pi/v2/index.json

    Args:
        package (str): Package name.
        standard_library (tuple): Standard library package names.
        target (str, optional): Target installation folder.

    Raises:
        JSONDecodeError: Failed to decode package info.
        StandardLibraryError: A standard library download was attempted.
        URLError: Request error raised by urllib.
    """

    package_index = PackageIndex()

    if not target.is_dir():
        raise FileNotFoundError(f"Project {str(target)} directory missing.")

    mpy_index = "https://micropython.org/pi/v2"
    try:
        package_url = f"{mpy_index}/package/py/{package}/latest.json"
        with urllib.request.urlopen(package_url) as r:
            package_info = json.loads(r.read())

        for file_path, file_hash in package_info.get("hashes", ()):
            file_path = pathlib.Path(file_path)
            if file_path.parent.name == "":
                name = file_path.name.replace(file_path.suffix, "")
            else:
                name = file_path.parent.name

            if name in package_index.standard_library:
                if name == package:
                    message = f"'{name}' in MicroPython standard library."
                    raise FileExistsError(message)
                continue

            file_url = f"{mpy_index}/file/{file_hash[:2]}/{file_hash}"
            with urllib.request.urlopen(file_url) as r:
                if r.status == 200:
                    output_path = target / file_path
                    if not file_path.parent.name == "":
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_bytes(r.read())
    except URLError as e:
        if e.status == 404:
            raise URLError(f"'{package}' not found in MicroPython index.")
        raise URLError(f"Unknown error - {e.status} | {e.reason}")
    except json.JSONDecodeError:
        raise
    except FileExistsError:
        raise
    except Exception as e:
        print(f"Uncaught Exception: {e}")
        print(traceback.format_exc())
