# Contribution Guidelines

All contributions are welcomed and appreciated.

## Raising Issues

A good bug report shouldn't leave any ambiguity as to how an issue/bug presents itself. Please describe the issue in detail in your report. Please complete the following steps in advance to help me fix any potential bugs/errors as fast as possible.

1. Check the version you are using.
2. Check the documentation for any issue related information.
3. Check the existing repository issue to prevent duplication of effort.
4. Collate information about the bug:
    1. Traceback details.
    2. OS, Platform & version (Windows, Linux etc.).
    3. Python version.
    4. Input and output.
    5. Reproducibility checks.

## Development Environment

Clone the repository:

    ```sh
    git clone git@github.com:andyrids/picoproject.git
    ```

Enter the repository directory:

    ```sh
    cd picoproject
    ```

### Installation with uv

**uv** is used as the Python package manager. To install **uv** see the installation
guide @ [uv documentation](https://docs.astral.sh/uv/getting-started/installation/).

Sync the project dependencies:

    ```sh
    uv sync
    ```

Activate the virtual environment created by uv:

    ```sh
    source .venv/bin/activate
    ```

### Installation without uv (pip)

Create a virtual environment:

    ```sh
    python -m venv .venv
    ```

Activate the virtual environment:

    ```sh
    source .venv/bin/activate
    ```

Install the project dependencies in editable mode with its optional dependencies:

    ```sh
    python -m pip install -e .[dev]
    ```

### Linting & Formatting

With the virtual environment activated the ruff check & format commands will implement the rules set in the pyproject.toml file. These tool can be also be run using the commands `uv run ruff check` or `uv run ruff format`.

To run the ruff linting tool, use the following command:

    ```sh
    (.venv) ruff check
    ```

To format the code in accordance with the project formatting rules, use the following command:

    ```sh
    (.venv) ruff format
    ```

### Commit Messages

Commit messages use the [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/#summary) specification:

`<type>[optional scope]: <description>`

    ```sh
    git commit -m "docs: update contribution guidelines."
    git commit -m "chore: ruff lint & format."
    git commit -m "feat: add new cli format command to format device filesystem."
    git commit -m "fix: patch an installation error for cli install command #1234."
    ```
A breaking change is indicated with a '!':

    ```sh
    git commit -m "refactor!: drop support for python 3.9."
    ```
