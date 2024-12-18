"""CLI command test functions.

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

Functions:
    test_compile_command: CLI compile command test function.
    test_install_command: CLI install command test function.
"""

import importlib.util
import pathlib
from typing import List

from picoproject.main import app
from picoproject.utils.progress import command
from rich.progress import Task
from typer.testing import CliRunner

runner = CliRunner()


def test_compile_command():
    """Test Typer CLI compile command."""

    target = pathlib.Path(__file__)
    compiled_target = target.with_suffix(".mpy")

    compile_args = ("compile", (target,))
    result = runner.invoke(app, compile_args, standalone_mode=False)

    # Result properties
    # exc_info, exception, exit_code output, return_value
    # runner, stderr, stderr_bytes, stdout, stdout_bytes

    tasks: List[Task] = result.return_value
    task, *_ = tasks
    assert task.finished
    assert not task.visible
    assert task.description == "Compiled"
    assert task.fields["item"].name == target.name
    assert compiled_target.is_file()

    compiled_target.unlink()
    command.remove_task(task.id)


def test_install_command(tmp_path: pathlib.Path) -> None:
    """Test Typer CLI install command."""

    tmp_path.mkdir(exist_ok=True)

    install_args = ("install", "umqtt.simple", "--directory", tmp_path.as_posix())
    result = runner.invoke(app, install_args, standalone_mode=False)

    tasks: List[Task] = result.return_value

    task, *_ = tasks
    assert task.finished
    assert not task.visible
    assert task.description == "Installed"
    command.remove_task(task.id)
