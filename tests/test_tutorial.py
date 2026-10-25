"""Tests for ``aamad tutorial``."""

from __future__ import annotations

from io import StringIO
from pathlib import Path

import pytest

from aamad.cli import main
from aamad.tutorial import (
    LESSONS,
    SAD_DECISION_HEADINGS,
    format_folder_hint,
    run_tutorial,
)
from aamad.validator import BUILD_ARTIFACTS, REVIEW_ARTIFACTS


class ScriptedPrompter:
    def __init__(self, answers: list[str | None]) -> None:
        self.answers = list(answers)

    def choose(self, message: str, options: list[tuple[str, str]]) -> str | None:
        if not self.answers:
            raise AssertionError(f"unexpected prompt: {message}")
        value = self.answers.pop(0)
        allowed = {item for item, _label in options}
        if value is not None and value not in allowed:
            raise AssertionError(f"{value!r} not in {allowed} for {message}")
        return value


def _write(path: Path, text: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sad() -> str:
    return "\n".join(SAD_DECISION_HEADINGS) + "\n"


def test_lesson_ids_are_unique_and_each_check_has_one_answer():
    ids = [lesson.id for lesson in LESSONS]
    assert len(ids) == len(set(ids))
    assert len(LESSONS) == 8
    for lesson in LESSONS:
        assert sum(choice.correct for choice in lesson.choices) == 1
        assert lesson.prompt
        assert lesson.body


def test_lessons_cover_the_spine():
    text = "\n".join(lesson.body for lesson in LESSONS)
    for phrase in (
        "*create-prd",
        "*review-codebase",
        "*select-pattern",
        "*run-evals",
        "*sync-docs",
        "aamad validate",
        "augmented call",
    ):
        assert phrase in text


def test_list_prints_ids(capsys: pytest.CaptureFixture[str]):
    assert main(["tutorial", "--list"]) == 0
    out = capsys.readouterr().out
    for lesson in LESSONS:
        assert lesson.id in out
        assert lesson.title in out


def test_non_tty_prints_study_sheet(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    assert main(["tutorial", "--dest", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "Lesson 1 of 8 — What AAMAD is" in out
    assert "Lesson 8 of 8 — What you run, and what you don't" in out
    assert "Answer:" in out
    assert "Where this folder stands" in out
    assert "not an AAMAD project yet" in out


def test_print_one_lesson(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    assert main(["tutorial", "--print", "--lesson", "practice", "--dest", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "Lesson 1 of 1 — What you run, and what you don't" in out
    assert "What AAMAD is" not in out
    assert "@product-mgr writes it in the IDE" in out


def test_unknown_lesson_is_rejected(capsys: pytest.CaptureFixture[str]):
    with pytest.raises(SystemExit) as exc:
        main(["tutorial", "--lesson", "nope"])
    assert exc.value.code == 2
    assert main(["tutorial", "--list"]) == 0


def test_run_tutorial_unknown_id_returns_2(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    assert run_tutorial(tmp_path, lesson_id="nope") == 2
    assert "Unknown lesson" in capsys.readouterr().err


def test_interactive_quit(tmp_path: Path):
    buffer = StringIO()
    code = run_tutorial(
        tmp_path,
        interactive=True,
        prompter=ScriptedPrompter(["quit"]),
        out=buffer,
    )
    assert code == 0
    text = buffer.getvalue()
    assert "Tutorial stopped." in text
    assert "Lesson 1 of" not in text


def test_interactive_wrong_answer_then_folder_hint(tmp_path: Path):
    buffer = StringIO()
    code = run_tutorial(
        tmp_path,
        lesson_id="what-aamad-is",
        interactive=True,
        prompter=ScriptedPrompter(["writes-prd", "done"]),
        out=buffer,
    )
    assert code == 0
    text = buffer.getvalue()
    assert "Not quite." in text
    assert "Copies the crew into the project" in text
    assert "Where this folder stands" in text


def test_interactive_walks_every_lesson(tmp_path: Path):
    answers: list[str | None] = ["all"]
    for lesson in LESSONS:
        answers.append(lesson.correct().value)
        answers.append("done" if lesson is LESSONS[-1] else "next")
    buffer = StringIO()
    code = run_tutorial(
        tmp_path,
        interactive=True,
        prompter=ScriptedPrompter(answers),
        out=buffer,
    )
    assert code == 0
    text = buffer.getvalue()
    assert "Not quite." not in text
    for lesson in LESSONS:
        assert lesson.title in text
    assert "Where this folder stands" in text


def test_interactive_jump_keeps_lesson_numbers(tmp_path: Path):
    buffer = StringIO()
    code = run_tutorial(
        tmp_path,
        interactive=True,
        prompter=ScriptedPrompter(["five-decisions", "workflow", "quit"]),
        out=buffer,
    )
    assert code == 0
    text = buffer.getvalue()
    assert "Lesson 6 of 8 — Five decisions before Build" in text
    assert "Tutorial stopped." in text


def test_interactive_cancel_stops(tmp_path: Path):
    buffer = StringIO()
    code = run_tutorial(
        tmp_path,
        interactive=True,
        prompter=ScriptedPrompter(["all", None]),
        out=buffer,
    )
    assert code == 0
    assert "Tutorial stopped." in buffer.getvalue()


def test_folder_hint_brownfield_starts_at_review(tmp_path: Path):
    _write(tmp_path / "aamad.config.yml", "project:\n  mode: brownfield\n")
    hint = format_folder_hint(tmp_path)
    assert "*review-codebase" in hint


def test_folder_hint_greenfield_starts_at_prd(tmp_path: Path):
    _write(tmp_path / "aamad.config.yml", "project:\n  mode: greenfield\n")
    hint = format_folder_hint(tmp_path)
    assert "*elicit-requirements" in hint


def test_folder_hint_names_missing_decision(tmp_path: Path):
    _write(tmp_path / "aamad.config.yml", "project:\n  mode: greenfield\n")
    _write(tmp_path / "project-context/1.define/prd.md", "# prd\n")
    _write(tmp_path / "project-context/1.define/sad.md", "Work Ownership\n")
    hint = format_folder_hint(tmp_path)
    assert "Pattern Decision" in hint


def test_folder_hint_follows_build_then_deliver(tmp_path: Path):
    _write(tmp_path / "aamad.config.yml", "project:\n  mode: greenfield\n")
    _write(tmp_path / "project-context/1.define/prd.md", "# prd\n")
    _write(tmp_path / "project-context/1.define/sad.md", _sad())
    hint = format_folder_hint(tmp_path)
    assert "*design-ux" in hint

    for relative in BUILD_ARTIFACTS:
        if relative.endswith("backend.md"):
            break
        _write(tmp_path / relative, "# done\n")
    hint = format_folder_hint(tmp_path)
    assert "backend.md" in hint

    for relative in BUILD_ARTIFACTS:
        _write(tmp_path / relative, "# done\n")
    hint = format_folder_hint(tmp_path)
    assert "*assess-security" in hint

    _write(tmp_path / "project-context/2.build/security.md", "# security\n")
    hint = format_folder_hint(tmp_path)
    assert "*prepare-release" in hint

    _write(tmp_path / "project-context/3.deliver/deploy.md", "# deploy\n")
    hint = format_folder_hint(tmp_path)
    assert "`aamad validate`" in hint


def test_folder_hint_brownfield_with_review_asks_for_prd(tmp_path: Path):
    _write(tmp_path / "aamad.config.yml", "project:\n  mode: brownfield\n")
    for relative in REVIEW_ARTIFACTS:
        _write(tmp_path / relative, "# review\n")
    hint = format_folder_hint(tmp_path)
    assert "constrained PRD" in hint


def test_folder_hint_unreadable_mode(tmp_path: Path):
    _write(tmp_path / "aamad.config.yml", "project: [\n")
    hint = format_folder_hint(tmp_path)
    assert "unreadable" in hint
