"""Exportation module which provides helper functions used when exporting the
project for distribution to a Raspberry Pi Pico device.

Functions:
    build_export_tree: Builds a Rich Tree instance representing export
        directory.
"""

import operator
import pathlib

from rich.filesize import decimal
from rich.text import Text
from rich.tree import Tree


def build_directory_tree(
    path: pathlib.Path, tree: Tree, precompiled: bool = False
) -> None:
    """Build a directory Tree recursively, using rich formatting.

    Args:
        path (Path): Root path for the directory tree.
        tree (Tree): Tree instance to modify.
        precompiled (bool): Highlight non-compiled files.
    """
    directory = operator.methodcaller("is_dir")
    python_file = operator.methodcaller("match", "*.py")

    sorted_paths = sorted(path.iterdir(), key=lambda x: x.is_file())
    for item in sorted_paths:
        if directory(item):
            branch = tree.add(f"[b bright_cyan]{item.name}")
            build_directory_tree(item, branch, precompiled)
        else:
            icon = "🐍" if python_file(item) else "📄"
            item_name = Text(f"{item.name}", "gray100")
            if precompiled and python_file(item):
                item_name.stylize("red strike")
            else:
                if item.stem == "__init__":
                    item_name.stylize("dim")
            # create file details branch
            details = Text(f"{icon} ")
            details.append(item_name)
            size = decimal(item.stat().st_size)
            details.append(f" ({size})", "gray62")
            # create entry in tree
            tree.add(details)
