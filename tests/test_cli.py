"""CLI tests for guided ``aamad init``."""

from __future__ import annotations

from pathlib import Path

import pytest

from aamad.cli import main
from aamad.onboarding import (
    NON_INTERACTIVE_MESSAGE,
    OnboardingNotInteractive,
    resolve_ide,
)


def test_resolve_ide_returns_provided_value():
    assert resolve_ide("kiro") == "kiro"


def test_resolve_ide_non_tty_raises():
    class FakeStdin:
        def isatty(self) -> bool:
            return False

    with pytest.raises(OnboardingNotInteractive, match="--ide"):
        resolve_ide(None, stdin=FakeStdin())


def test_resolve_ide_prompts_when_tty(monkeypatch):
    monkeypatch.setattr("aamad.onboarding.ask_development_environment", lambda: "vscode")

    class FakeStdin:
        def isatty(self) -> bool:
            return True

    assert resolve_ide(None, stdin=FakeStdin()) == "vscode"


def test_init_with_ide_skips_prompt(monkeypatch, tmp_path: Path):
    called: dict = {}

    def fake_extract(**kwargs):
        called.update(kwargs)
        return [tmp_path / "AGENTS.md"]

    def fail_ask():
        raise AssertionError("should not prompt when --ide is set")

    monkeypatch.setattr("aamad.cli.extract_artifacts", fake_extract)
    monkeypatch.setattr("aamad.onboarding.ask_development_environment", fail_ask)

    rc = main(["init", "--dest", str(tmp_path), "--ide", "kiro", "--dry-run"])
    assert rc == 0
    assert called["ide"] == "kiro"
    assert called["dry_run"] is True


def test_init_menu_selection_calls_extract(monkeypatch, tmp_path: Path):
    called: dict = {}

    def fake_extract(**kwargs):
        called.update(kwargs)
        return []

    monkeypatch.setattr("aamad.cli.extract_artifacts", fake_extract)
    monkeypatch.setattr("aamad.onboarding.ask_development_environment", lambda: "kiro")

    class FakeStdin:
        def isatty(self) -> bool:
            return True

    monkeypatch.setattr("aamad.onboarding.sys.stdin", FakeStdin())

    rc = main(["init", "--dest", str(tmp_path), "--dry-run"])
    assert rc == 0
    assert called["ide"] == "kiro"


def test_init_non_tty_without_ide_exits_2(monkeypatch, tmp_path: Path, capsys):
    class FakeStdin:
        def isatty(self) -> bool:
            return False

    monkeypatch.setattr("aamad.onboarding.sys.stdin", FakeStdin())

    def fail_extract(**kwargs):
        raise AssertionError("should not extract without an IDE")

    monkeypatch.setattr("aamad.cli.extract_artifacts", fail_extract)

    rc = main(["init", "--dest", str(tmp_path)])
    assert rc == 2
    captured = capsys.readouterr()
    assert "--ide" in captured.err
    assert NON_INTERACTIVE_MESSAGE in captured.err
