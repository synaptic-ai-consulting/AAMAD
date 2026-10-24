"""Guided project-level setup questions for ``aamad init``.

Release 0.9.0 asks only for the development environment. Later releases can
append questions here without changing the CLI surface.
"""

from __future__ import annotations

import sys
from typing import TextIO

IDE_CHOICES = ["cursor", "claude-code", "vscode", "kiro"]

IDE_OPTIONS = [
    ("cursor", "Cursor"),
    ("claude-code", "Claude Code"),
    ("vscode", "VS Code with GitHub Copilot"),
    ("kiro", "Kiro"),
]

PROMPT_IDE = "Which development environment will you use the AAMAD dev crew on?"

NON_INTERACTIVE_MESSAGE = (
    "aamad init needs a development environment. "
    "Pass --ide {cursor,claude-code,vscode,kiro} when not running interactively."
)


class OnboardingCancelled(Exception):
    """Raised when the operator cancels an onboarding prompt."""


class OnboardingNotInteractive(Exception):
    """Raised when a prompt is required but stdin is not a TTY."""


def ask_development_environment() -> str:
    """Show an arrow-key menu of supported IDEs and return the selected value."""
    import questionary

    choices = [
        questionary.Choice(title=label, value=value) for value, label in IDE_OPTIONS
    ]
    result = questionary.select(PROMPT_IDE, choices=choices).ask()
    if result is None:
        raise OnboardingCancelled("Init cancelled.")
    return result


def resolve_ide(ide: str | None, *, stdin: TextIO | None = None) -> str:
    """Return ``ide`` when provided; otherwise prompt, or fail when not a TTY."""
    if ide:
        return ide
    stream = stdin if stdin is not None else sys.stdin
    if not stream.isatty():
        raise OnboardingNotInteractive(NON_INTERACTIVE_MESSAGE)
    return ask_development_environment()
