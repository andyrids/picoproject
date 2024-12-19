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
import operator
import pathlib
import shutil
from typing import List

from rich.progress import Task
from typer.testing import CliRunner

from picoproject.main import app
from picoproject.utils.progress import command
from picoproject.utils.project import ProjectPath

runner = CliRunner()


def test_compile_command():
    """Test Typer CLI compile command."""

    target = pathlib.Path(__file__)
    compiled_target = target.with_suffix(".mpy")

    args = ("compile", (target,))
    result = runner.invoke(app, args, standalone_mode=False)

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

    args = ("install", "umqtt.simple", "--directory", tmp_path.as_posix())
    result = runner.invoke(app, args, standalone_mode=False)

    tasks: List[Task] = result.return_value
    task, *_ = tasks
    assert task.finished
    assert not task.visible
    assert task.description == "Installed"
    command.remove_task(task.id)

    # umqtt.simple23 not found in MicroPython Index
    args = ("install", "umqtt.simple23", "--directory", tmp_path.as_posix())
    result = runner.invoke(app, args, standalone_mode=False)

    tasks: List[Task] = result.return_value
    task, *_ = tasks
    assert not task.finished
    assert task.visible
    assert task.description == "Error"
    command.remove_task(task.id)

    # base64 in MicroPython standard library
    args = ("install", "base64", "--directory", tmp_path.as_posix())
    result = runner.invoke(app, args, standalone_mode=False)

    tasks: List[Task] = result.return_value
    task, *_ = tasks
    assert not task.finished
    assert task.visible
    assert task.description == "Error"
    command.remove_task(task.id)


def test_export_command() -> None:
    """Test Typer CLI export command."""
    args = ("export",)
    result = runner.invoke(app, args, standalone_mode=False)
    tasks: List[Task] = result.return_value

    visible = operator.attrgetter("visible")
    assert not any(map(visible, tasks))

    project = ProjectPath()
    export_paths = tuple(project.export / i.fields["item"] for i in tasks)
    is_file = operator.methodcaller("is_file")
    assert all(map(is_file, export_paths))

    shutil.rmtree(project.export)

    for task in tasks:
        command.remove_task(task.id)
