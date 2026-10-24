"""Guided project-level setup questions for ``aamad init``.

Asks for the development environment, then greenfield vs brownfield.
Greenfield also asks which runtime adapter to use (or choose later).
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

MODE_CHOICES = ["greenfield", "brownfield"]

MODE_OPTIONS = [
    ("greenfield", "Greenfield — start from scratch"),
    ("brownfield", "Brownfield — this repo already contains an ongoing project"),
]

DEFAULT_MODE = "greenfield"

RUNTIME_CHOICES = ["crewai", "claude-agent-sdk", "cursor-sdk", "later"]

RUNTIME_OPTIONS = [
    ("crewai", "CrewAI"),
    ("claude-agent-sdk", "Claude Agent SDK"),
    ("cursor-sdk", "Cursor SDK"),
    ("later", "Choose this later"),
]

DEFAULT_RUNTIME = "later"

PROMPT_IDE = "Which development environment will you use the AAMAD dev crew on?"

PROMPT_MODE = "Is this a greenfield or a brownfield project?"

PROMPT_RUNTIME = "Which runtime adapter will this project use?"

DEFERRED_RUNTIME_MESSAGE = (
    "CrewAI will be used as the default runtime if you do not set "
    "AAMAD_TARGET_RUNTIME later."
)

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


def ask_project_mode() -> str:
    """Show an arrow-key menu of project modes and return the selected value."""
    import questionary

    choices = [
        questionary.Choice(title=label, value=value) for value, label in MODE_OPTIONS
    ]
    result = questionary.select(PROMPT_MODE, choices=choices).ask()
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


def resolve_mode(mode: str | None, *, stdin: TextIO | None = None) -> str:
    """Return ``mode`` when provided; otherwise prompt, or default when not a TTY."""
    if mode:
        return mode
    stream = stdin if stdin is not None else sys.stdin
    if not stream.isatty():
        return DEFAULT_MODE
    return ask_project_mode()


def ask_runtime() -> str:
    """Show an arrow-key menu of runtime adapters and return the selected value."""
    import questionary

    choices = [
        questionary.Choice(title=label, value=value) for value, label in RUNTIME_OPTIONS
    ]
    result = questionary.select(PROMPT_RUNTIME, choices=choices).ask()
    if result is None:
        raise OnboardingCancelled("Init cancelled.")
    return result


def resolve_runtime(
    runtime: str | None,
    mode: str,
    *,
    stdin: TextIO | None = None,
) -> str:
    """Return a runtime choice for greenfield init; skip prompting on brownfield."""
    if runtime:
        return runtime
    if mode != "greenfield":
        return DEFAULT_RUNTIME
    stream = stdin if stdin is not None else sys.stdin
    if not stream.isatty():
        return DEFAULT_RUNTIME
    return ask_runtime()
