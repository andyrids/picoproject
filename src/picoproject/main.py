"""Main module for Typer CLI, containing app instance and CLI commands.

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
    cross_compile: Compilation command for CLI.
    export: Project distribution interface for CLI.
    install: Package installation interface for CLI.
"""

import contextlib
import functools
import json
import operator
import pathlib
import subprocess
import time
from itertools import filterfalse
from typing import List, Optional
from urllib.error import URLError

import mpy_cross
import typer
from rich.columns import Columns
from rich.panel import Panel
from rich.progress import Task
from rich.tree import Tree
from typing_extensions import Annotated

from .utils.exceptions import CompilationError
from .utils.exportation import build_directory_tree
from .utils.installation import download_mpy_package
from .utils.progress import command, commands, progress_display, progress_panel
from .utils.project import ProjectPath

config_file = pathlib.Path(__file__).parent / "config" / "commands.json"
config = json.loads(config_file.read_bytes())

app = typer.Typer(**config["typer"])


@app.command("compile", **config["compile"])
def cross_compile(
    targets: Annotated[
        Optional[tuple[pathlib.Path]],
        typer.Argument(
            help="Python [b purple]compilation[/b purple] targets.",
            show_default="All Python files",
        ),
    ] = None,
) -> List[Task]:
    """[b purple]Compile[/b purple] [i]TARGETS[/i] to MicroPython binary files
    (mpy-cross).
    """

    compiler_args = ("-march=armv6m",)
    popen_kwargs = {"stderr": subprocess.PIPE, "universal_newlines": True}
    compiler = functools.partial(mpy_cross.run, *compiler_args, **popen_kwargs)
    compiled = operator.methodcaller("with_suffix", ".mpy")

    project = ProjectPath()
    targets = project.python if targets is None else targets

    with contextlib.ExitStack() as cm:
        update_commands = False
        if progress_display.is_started:
            commands_id, *_ = commands.task_ids
        else:
            progress_panel.title = "[b]Compilation Progress"
            cm.enter_context(progress_display)
            commands_id = commands.add_task("", total=len(targets))
            commands.start_task(commands_id)
            update_commands = True
            map(command.remove_task, command.task_ids)

        for item in targets:
            name = item.relative_to(project.package, walk_up=True)
            try:
                command_id = command.add_task("Compiling", item=name, total=1)
                process: subprocess.Popen = compiler(item)
                stdout, stderr = process.communicate(timeout=5)
                if process.returncode:
                    raise CompilationError(str(name))
                while not compiled(item).exists():
                    time.sleep(1)
            except CompilationError:
                commands.console.log(f"[b red]Compilation error for {name}")
                command.update(command_id, description="Error")
            except subprocess.TimeoutExpired:
                process.kill()
                commands.console.log(f"[b red]Compilation timed out")
            except Exception as e:
                commands.console.log(f"[b red]Unhandled error: {e}")
                command.update(command_id, description="Error")
            # no exceptions raised
            else:
                command.update(command_id, description="Compiled", advance=1)
                commands.update(commands_id, advance=update_commands)
            # before end of try
            finally:
                command.stop_task(command_id)
        # hide successful tasks
        for task in filter(operator.attrgetter("finished"), command.tasks):
            command.update(task.id, visible=False)
        commands.console.log("[b green]Compilation tasks completed")
        # for PyTest functions
        return command.tasks


@app.command("install", **config["install"])
def install(
    packages: Annotated[
        List[str],
        typer.Argument(
            help="MicroPython packages to be [b blue]installed[/b blue]",
            show_default=False,
        ),
    ],
    directory: Annotated[
        Optional[pathlib.Path],
        typer.Option(
            help="Target [b blue]installation[/b blue] path",
            show_default=False,
        ),
    ] = None,
) -> List[Task]:
    """[b blue]Install[/b blue] MicroPython [i]PACKAGES[/i] locally (mip)."""

    with contextlib.ExitStack() as cm:
        update_commands = False
        if progress_display.is_started:
            commands_id, *_ = commands.task_ids
        else:
            progress_panel.title = "[b]Installation Progress"
            cm.enter_context(progress_display)
            commands_id = commands.add_task("", total=len(packages))
            commands.start_task(commands_id)
            update_commands = True
            map(command.remove_task, command.task_ids)

        project = ProjectPath()
        directory = project.lib if directory is None else directory
        for item in packages:
            command_id = command.add_task("Installing", item=item, total=1)
            try:
                download_mpy_package(item, directory)
            except (FileNotFoundError, FileExistsError) as e:
                command.update(command_id, description="Error")
                commands.console.log(f"[b bright_red]{e}")
            except URLError as e:
                command.update(command_id, description="Error")
                commands.console.log(f"[b bright_red]{e.reason}")
            # no exceptions raised
            else:
                command.update(command_id, description="Installed", advance=1)
                commands.update(commands_id, advance=update_commands)
            # before end of try
            finally:
                command.stop_task(command_id)
        # hide successful tasks
        for task in filter(operator.attrgetter("finished"), command.tasks):
            command.update(task.id, visible=False)
        # for PyTest functions
        return command.tasks


@app.command("export", **config["export"])
def export(
    precompiled: Annotated[
        Optional[bool],
        typer.Option(
            "--precompiled",
            help="Only [b green]export[/b green] precompiled code.",
        ),
    ] = None,
):
    """[b green]Export[/b green] project files for distribution."""

    project = ProjectPath()
    exports = project.package.rglob("*.*")
    exports = sorted(filterfalse(lambda x: x.match("*.pyc"), exports))

    with contextlib.ExitStack() as cm:
        update_commands = False
        if progress_display.is_started:
            commands_id, *_ = commands.task_ids
        else:
            progress_panel.title = "[b]Exportation Progress"
            cm.enter_context(progress_display)
            commands_id = commands.add_task("", total=len(exports))
            commands.start_task(commands_id)
            update_commands = True
            map(command.remove_task, command.task_ids)

        try:
            project.export.mkdir()
        except FileExistsError:
            pass

        cpython_file = operator.methodcaller("match", "*.pyc")
        python_file = operator.methodcaller("match", "*.py")
        micropython_version = operator.methodcaller("with_suffix", ".mpy")

        commands_total = len(exports)
        for item in exports:
            item_name = item.relative_to(project.package)
            command_id = command.add_task("Exporting", item=item_name, total=1)

            item_export = project.export / item_name
            item_export.parent.mkdir(parents=True, exist_ok=True)
            if precompiled:
                if python_file(item):
                    # remove previous export
                    if item_export.exists():
                        item_export.unlink()
                    # check for precompiled version
                    item_compiled = micropython_version(item)
                    if item_compiled.exists():
                        commands_total -= 1
                        command.stop_task(command_id)
                        commands.update(commands_id, total=commands_total)
                        continue
                    # compile item (precompiled version missing)
                    cross_compile(targets=(item,))
                    # if successfully compiled
                    if item_compiled.exists():
                        command.stop_task(command_id)

                        # convert Python item_name path suffix
                        item_name = micropython_version(item_name)
                        command_id = command.add_task(
                            "Exporting", item=item_name, total=1
                        )

                        # convert Python item_export path suffix
                        item_export = micropython_version(item_export)
                        item_export.write_bytes(item_compiled.read_bytes())

                        description = "Exported/Compiled"
                        command.update(
                            command_id, description=description, advance=1
                        )
                        commands.update(commands_id, advance=update_commands)
                        continue
                    # precompiled version missing & compilation failed
                    command.stop_task(command_id)
                    command.update(command_id, description="Error")

            item_export.write_bytes(item.read_bytes())
            command.update(command_id, description="Exported", advance=1)
            commands.update(commands_id, advance=update_commands)
        # hide successful tasks
        for task in filter(operator.attrgetter("finished"), command.tasks):
            command.update(task.id, visible=False)

    # generate directory tree for exported files
    tree_label = f"[b bright_cyan]{project.root.name}/export"
    export_tree = Tree(tree_label, guide_style="dark_slate_gray3")
    build_directory_tree(project.export, export_tree, precompiled)

    # generate directory tree for project files
    tree_label = f"[b bright_cyan]{project.package.relative_to(project.root)}"
    project_tree = Tree(tree_label, guide_style="dark_slate_gray3")
    build_directory_tree(project.package, project_tree, precompiled)

    commands.console.print(
        Columns(
            (
                Panel(project_tree, title="[b]Project Files", width=74),
                Panel(export_tree, title="[b]Exported Files", width=74),
            ),
            equal=True,
            align="center",
        ),
        new_line_start=True,
    )

    # for PyTest functions
    return command.tasks


if __name__ == "__main__":
    # python -m command_line.main install umqtt.simple umqtt.robust
    # uv run CLI install umqtt.simple umqtt.robust aioble urequests
    app()
