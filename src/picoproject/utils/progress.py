"""Progress module contains helper classes and functions for working with
rich Progress instances within the Typer CLI commands.

Classes:
    ProgressColour: Highlights Progress Task text based on regex patterns.

Exceptions:
    StandardLibraryError: Raised when installing packages already in standard
        library.
"""

from rich.columns import Columns
from rich.console import Group
from rich.highlighter import Highlighter
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn, TimeElapsedColumn
from rich.rule import Rule
from rich.text import Text


class Singleton(object):
    """Facilitates singleton pattern."""

    def __new__(cls, *args, **kwargs):
        """
        >>> s = Singleton()
        >>> p = Singleton()
        >>> id(s) == id(p)
        True
        """

        it_id = "__it__"
        # __dict__ must be used instead of getattr
        it = cls.__dict__.get(it_id, None)
        if it is not None:
            return it
        it = object.__new__(cls)
        setattr(cls, it_id, it)
        it.init(*args, **kwargs)
        return it

    def init(self, *args, **kwargs):
        """Initialise Singleton class"""

        pass


class ProgressColour(Highlighter):
    """Custom rich text Highlighter class."""

    def highlight(self, text: Text) -> None:
        """Highlight text based on task description.

        Args:
            text (Text): Task text for highlighting.

        Returns:
            None
        """

        regex_styles = (
            (
                r"(?P<status>(Compiling|Exporting|Installing|Formatting).+)",
                "magenta",
            ),
            (
                r"(?P<status>(Compiled|Exported|Installed|Formatted).+)",
                "bright_green",
            ),
            (r"(?P<status>Error.+)", "bright_red"),
        )

        for regex, colour in regex_styles:
            if text.highlight_regex(regex, colour, style_prefix="b"):
                return


def new_command_progress() -> Progress:
    """Create a Progress instance for use by a Typer CLI command.

    Returns:
        A Progress instance.
    """
    task_details = "{task.description} {task.fields[item]}"
    return Progress(
        TextColumn(task_details, highlighter=ProgressColour()),
        BarColumn(bar_width=None),
        "{task.percentage:.0f}%",
    )


command = new_command_progress()

commands = Progress(
    TimeElapsedColumn(),
    BarColumn(bar_width=None),
    TextColumn("[{task.completed}/{task.total}]"),
    expand=True,
)

progress_panel = Panel(
    Group(
        command,
        Rule("", style="#AAAAAA"),
        commands,
    ),
    title="",
    expand=False,
    width=150,
)

progress_display = Live(
    Columns([progress_panel]),
)
