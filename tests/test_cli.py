"""CLI tests for guided ``aamad init``."""

from __future__ import annotations

from pathlib import Path

import pytest

from aamad.cli import format_next_steps, format_runtime_note, main
from aamad.onboarding import (
    DEFAULT_MODE,
    DEFAULT_RUNTIME,
    DEFERRED_RUNTIME_MESSAGE,
    NON_INTERACTIVE_MESSAGE,
    OnboardingCancelled,
    OnboardingNotInteractive,
    resolve_ide,
    resolve_mode,
    resolve_runtime,
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


def test_resolve_mode_returns_provided_value():
    assert resolve_mode("brownfield") == "brownfield"


def test_resolve_mode_non_tty_defaults_greenfield():
    class FakeStdin:
        def isatty(self) -> bool:
            return False

    assert resolve_mode(None, stdin=FakeStdin()) == DEFAULT_MODE


def test_resolve_mode_prompts_when_tty(monkeypatch):
    monkeypatch.setattr("aamad.onboarding.ask_project_mode", lambda: "brownfield")

    class FakeStdin:
        def isatty(self) -> bool:
            return True

    assert resolve_mode(None, stdin=FakeStdin()) == "brownfield"


def test_resolve_runtime_returns_provided_value():
    assert resolve_runtime("cursor-sdk", "greenfield") == "cursor-sdk"


def test_resolve_runtime_skips_prompt_on_brownfield(monkeypatch):
    def fail_ask():
        raise AssertionError("should not prompt for runtime on brownfield")

    monkeypatch.setattr("aamad.onboarding.ask_runtime", fail_ask)

    class FakeStdin:
        def isatty(self) -> bool:
            return True

    assert resolve_runtime(None, "brownfield", stdin=FakeStdin()) == DEFAULT_RUNTIME


def test_resolve_runtime_honors_flag_on_brownfield():
    assert resolve_runtime("crewai", "brownfield") == "crewai"


def test_resolve_runtime_non_tty_defaults_later():
    class FakeStdin:
        def isatty(self) -> bool:
            return False

    assert resolve_runtime(None, "greenfield", stdin=FakeStdin()) == DEFAULT_RUNTIME


def test_resolve_runtime_prompts_when_tty(monkeypatch):
    monkeypatch.setattr("aamad.onboarding.ask_runtime", lambda: "claude-agent-sdk")

    class FakeStdin:
        def isatty(self) -> bool:
            return True

    assert resolve_runtime(None, "greenfield", stdin=FakeStdin()) == "claude-agent-sdk"


def test_init_with_ide_skips_ide_prompt(monkeypatch, tmp_path: Path):
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
    assert called["mode"] == "greenfield"
    assert called["runtime"] == "later"
    assert called["dry_run"] is True


def test_init_with_mode_skips_mode_prompt(monkeypatch, tmp_path: Path):
    called: dict = {}

    def fake_extract(**kwargs):
        called.update(kwargs)
        return []

    def fail_mode():
        raise AssertionError("should not prompt when --mode is set")

    def fail_runtime():
        raise AssertionError("should not prompt for runtime on brownfield")

    monkeypatch.setattr("aamad.cli.extract_artifacts", fake_extract)
    monkeypatch.setattr("aamad.onboarding.ask_project_mode", fail_mode)
    monkeypatch.setattr("aamad.onboarding.ask_runtime", fail_runtime)

    rc = main(
        [
            "init",
            "--dest",
            str(tmp_path),
            "--ide",
            "cursor",
            "--mode",
            "brownfield",
            "--dry-run",
        ]
    )
    assert rc == 0
    assert called["ide"] == "cursor"
    assert called["mode"] == "brownfield"
    assert called["runtime"] == "later"


def test_init_menu_selection_calls_extract(monkeypatch, tmp_path: Path):
    called: dict = {}

    def fake_extract(**kwargs):
        called.update(kwargs)
        return []

    def fail_runtime():
        raise AssertionError("should not prompt for runtime on brownfield")

    monkeypatch.setattr("aamad.cli.extract_artifacts", fake_extract)
    monkeypatch.setattr("aamad.onboarding.ask_development_environment", lambda: "kiro")
    monkeypatch.setattr("aamad.onboarding.ask_project_mode", lambda: "brownfield")
    monkeypatch.setattr("aamad.onboarding.ask_runtime", fail_runtime)

    class FakeStdin:
        def isatty(self) -> bool:
            return True

    monkeypatch.setattr("aamad.onboarding.sys.stdin", FakeStdin())

    rc = main(["init", "--dest", str(tmp_path), "--dry-run"])
    assert rc == 0
    assert called["ide"] == "kiro"
    assert called["mode"] == "brownfield"


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


def test_format_next_steps_brownfield_cursor():
    text = format_next_steps("cursor", "brownfield")
    assert "Next steps (brownfield):" in text
    assert "@system.arch" in text
    assert "*review-codebase" in text
    assert "Operator Decision" in text


def test_format_next_steps_greenfield_claude():
    text = format_next_steps("claude-code", "greenfield")
    assert "Next steps (greenfield):" in text
    assert "/phase-1-define" in text
    assert "*create-prd" in text


def test_init_prints_next_steps(monkeypatch, tmp_path: Path, capsys):
    monkeypatch.setattr("aamad.cli.extract_artifacts", lambda **kwargs: [])

    rc = main(
        [
            "init",
            "--dest",
            str(tmp_path),
            "--ide",
            "kiro",
            "--mode",
            "brownfield",
            "--dry-run",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "Next steps (brownfield):" in out
    assert "/phase-0-review" in out


def test_init_mode_cancel_exits_2(monkeypatch, tmp_path: Path):
    def cancel():
        raise OnboardingCancelled("Init cancelled.")

    monkeypatch.setattr("aamad.onboarding.ask_project_mode", cancel)

    class FakeStdin:
        def isatty(self) -> bool:
            return True

    monkeypatch.setattr("aamad.onboarding.sys.stdin", FakeStdin())

    rc = main(["init", "--dest", str(tmp_path), "--ide", "cursor"])
    assert rc == 2


def test_init_with_runtime_skips_runtime_prompt(monkeypatch, tmp_path: Path, capsys):
    called: dict = {}

    def fake_extract(**kwargs):
        called.update(kwargs)
        return []

    def fail_runtime():
        raise AssertionError("should not prompt when --runtime is set")

    monkeypatch.setattr("aamad.cli.extract_artifacts", fake_extract)
    monkeypatch.setattr("aamad.onboarding.ask_runtime", fail_runtime)

    rc = main(
        [
            "init",
            "--dest",
            str(tmp_path),
            "--ide",
            "cursor",
            "--mode",
            "greenfield",
            "--runtime",
            "cursor-sdk",
            "--dry-run",
        ]
    )
    assert rc == 0
    assert called["runtime"] == "cursor-sdk"
    out = capsys.readouterr().out
    assert "AAMAD_TARGET_RUNTIME set to cursor-sdk." in out


def test_init_greenfield_prints_deferred_runtime_note(monkeypatch, tmp_path: Path, capsys):
    monkeypatch.setattr("aamad.cli.extract_artifacts", lambda **kwargs: [])

    rc = main(
        [
            "init",
            "--dest",
            str(tmp_path),
            "--ide",
            "cursor",
            "--mode",
            "greenfield",
            "--runtime",
            "later",
            "--dry-run",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert DEFERRED_RUNTIME_MESSAGE in out


def test_init_menu_greenfield_asks_runtime(monkeypatch, tmp_path: Path):
    called: dict = {}

    def fake_extract(**kwargs):
        called.update(kwargs)
        return []

    monkeypatch.setattr("aamad.cli.extract_artifacts", fake_extract)
    monkeypatch.setattr("aamad.onboarding.ask_development_environment", lambda: "cursor")
    monkeypatch.setattr("aamad.onboarding.ask_project_mode", lambda: "greenfield")
    monkeypatch.setattr("aamad.onboarding.ask_runtime", lambda: "crewai")

    class FakeStdin:
        def isatty(self) -> bool:
            return True

    monkeypatch.setattr("aamad.onboarding.sys.stdin", FakeStdin())

    rc = main(["init", "--dest", str(tmp_path), "--dry-run"])
    assert rc == 0
    assert called["ide"] == "cursor"
    assert called["mode"] == "greenfield"
    assert called["runtime"] == "crewai"


def test_format_runtime_note_later():
    assert format_runtime_note("later") == DEFERRED_RUNTIME_MESSAGE


def test_format_runtime_note_selected():
    assert format_runtime_note("crewai") == "AAMAD_TARGET_RUNTIME set to crewai."


def test_init_runtime_cancel_exits_2(monkeypatch, tmp_path: Path):
    def cancel():
        raise OnboardingCancelled("Init cancelled.")

    monkeypatch.setattr("aamad.onboarding.ask_runtime", cancel)

    class FakeStdin:
        def isatty(self) -> bool:
            return True

    monkeypatch.setattr("aamad.onboarding.sys.stdin", FakeStdin())

    rc = main(
        ["init", "--dest", str(tmp_path), "--ide", "cursor", "--mode", "greenfield"]
    )
    assert rc == 2
