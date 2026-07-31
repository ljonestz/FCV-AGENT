"""Prepare the pinned Climate-FCV bank and install Render dependencies."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys


REPOSITORY_ROOT = Path(__file__).resolve().parent


def build_commands(python_executable: str) -> list[list[str]]:
    """Return the ordered, auditable commands for a Render build."""

    return [
        ["git", "submodule", "sync", "--recursive"],
        ["git", "submodule", "update", "--init", "--recursive"],
        [
            python_executable,
            "-m",
            "pip",
            "install",
            "-r",
            "requirements.txt",
        ],
    ]


def main() -> int:
    """Initialize the pinned public bank before installing the application."""

    for command in build_commands(sys.executable):
        subprocess.run(command, cwd=REPOSITORY_ROOT, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
