"""Tests for aamad validate quality gates."""

from __future__ import annotations

from pathlib import Path

import pytest

from aamad.cli import main
from aamad.validator import format_report, validate_project

TERMINAL = """
## Sources
- test

## Assumptions
- none

## Open Questions
- none

## Audit
- AAMAD_TARGET_RUNTIME: crewai
- persona: test
"""


def _write(path: Path, body: str = "# Doc\n\n" + TERMINAL) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


@pytest.fixture
def project(tmp_path: Path) -> Path:
    return tmp_path


def test_define_requires_prd_and_sad(project: Path) -> None:
    result = validate_project(project, phase="define")
    assert not result.ok
    paths = {i.path for i in result.issues if i.level == "error"}
    assert "project-context/1.define/prd.md" in paths
    assert "project-context/1.define/sad.md" in paths


def test_define_passes_with_terminal_sections(project: Path) -> None:
    _write(project / "project-context/1.define/prd.md")
    _write(project / "project-context/1.define/sad.md")
    result = validate_project(project, phase="define")
    assert result.ok, format_report(result)


def test_missing_heading_is_error(project: Path) -> None:
    _write(
        project / "project-context/1.define/prd.md",
        "# PRD\n\n## Sources\n\n## Assumptions\n\n## Open Questions\n",
    )
    _write(project / "project-context/1.define/sad.md")
    result = validate_project(project, phase="define")
    assert not result.ok
    assert any("Audit" in i.message for i in result.issues)


def test_deliver_requires_qa_gate(project: Path) -> None:
    _write(project / "project-context/1.define/prd.md")
    _write(project / "project-context/1.define/sad.md")
    _write(project / "project-context/3.deliver/deploy.md")
    result = validate_project(project, phase="deliver")
    assert not result.ok
    assert any("qa.md" in i.path for i in result.issues if i.level == "error")


def test_deliver_passes_with_qa_and_deploy(project: Path) -> None:
    _write(project / "project-context/1.define/prd.md")
    _write(project / "project-context/1.define/sad.md")
    for name in ("setup.md", "frontend.md", "backend.md", "integration.md", "qa.md"):
        _write(project / "project-context/2.build" / name)
    _write(project / "project-context/3.deliver/deploy.md")
    result = validate_project(project, phase="deliver")
    assert result.ok, format_report(result)


def test_cli_validate_exit_codes(project: Path) -> None:
    assert main(["validate", "--dest", str(project), "--phase", "define"]) == 1
    _write(project / "project-context/1.define/prd.md")
    _write(project / "project-context/1.define/sad.md")
    assert main(["validate", "--dest", str(project), "--phase", "define"]) == 0


def test_mrd_optional_warns_only(project: Path) -> None:
    _write(project / "project-context/1.define/prd.md")
    _write(project / "project-context/1.define/sad.md")
    result = validate_project(project, phase="define")
    assert result.ok
    assert any(
        i.level == "warning" and i.path.endswith("mrd.md") for i in result.issues
    )


def test_evals_optional_warns_only(project: Path) -> None:
    _write(project / "project-context/1.define/prd.md")
    _write(project / "project-context/1.define/sad.md")
    for name in ("setup.md", "frontend.md", "backend.md", "integration.md", "qa.md"):
        _write(project / "project-context/2.build" / name)
    result = validate_project(project, phase="build")
    assert result.ok, format_report(result)
    assert any(
        i.level == "warning" and i.path.endswith("evals.md") for i in result.issues
    )


def test_evals_present_checks_terminal_sections(project: Path) -> None:
    _write(project / "project-context/1.define/prd.md")
    _write(project / "project-context/1.define/sad.md")
    for name in ("setup.md", "frontend.md", "backend.md", "integration.md", "qa.md"):
        _write(project / "project-context/2.build" / name)
    _write(project / "project-context/2.build/evals.md", "# Evals\n\nIncomplete.\n")
    result = validate_project(project, phase="build")
    assert not result.ok
    assert any("evals.md" in i.path for i in result.issues if i.level == "error")


def test_evals_present_with_terminal_sections_passes(project: Path) -> None:
    _write(project / "project-context/1.define/prd.md")
    _write(project / "project-context/1.define/sad.md")
    for name in ("setup.md", "frontend.md", "backend.md", "integration.md", "qa.md", "evals.md"):
        _write(project / "project-context/2.build" / name)
    result = validate_project(project, phase="build")
    assert result.ok, format_report(result)
    assert not any(i.path.endswith("evals.md") for i in result.issues)


def test_unknown_config_key_is_error(project: Path) -> None:
    _write(project / "project-context/1.define/prd.md")
    _write(project / "project-context/1.define/sad.md")
    (project / "aamad.config.yml").write_text(
        "version: 1\nnot_a_real_section: true\n", encoding="utf-8"
    )
    result = validate_project(project, phase="define")
    assert not result.ok
    assert any("Unknown top-level" in i.message for i in result.issues)


def test_valid_config_passes(project: Path) -> None:
    _write(project / "project-context/1.define/prd.md")
    _write(project / "project-context/1.define/sad.md")
    (project / "aamad.config.yml").write_text(
        "version: 1\nruntime:\n  target: crewai\n", encoding="utf-8"
    )
    result = validate_project(project, phase="define")
    assert result.ok, format_report(result)


def test_project_mode_config_key_is_known(project: Path) -> None:
    _write(project / "project-context/1.define/prd.md")
    _write(project / "project-context/1.define/sad.md")
    (project / "aamad.config.yml").write_text(
        "version: 1\nproject:\n  mode: greenfield\n", encoding="utf-8"
    )
    result = validate_project(project, phase="define")
    assert result.ok, format_report(result)


def _write_review_artifacts(project: Path, *, status: str = "pending") -> None:
    for name in ("current-state.md", "documentation.md", "architecture-backlog.md"):
        _write(project / "project-context/0.review" / name)
    _write(
        project / "project-context/1.define/sad.md",
        "# SAD\n\n"
        "## Proposed Enhancements\n- ARCH-001\n\n"
        f"## Operator Decision\n- Status: {status}\n\n"
        + TERMINAL,
    )


def test_review_requires_artifacts(project: Path) -> None:
    result = validate_project(project, phase="review")
    assert not result.ok
    paths = {i.path for i in result.issues if i.level == "error"}
    assert "project-context/0.review/current-state.md" in paths
    assert "project-context/1.define/sad.md" in paths


def test_review_passes_with_pending_decision(project: Path) -> None:
    _write_review_artifacts(project, status="pending")
    result = validate_project(project, phase="review")
    assert result.ok, format_report(result)


def test_review_sad_missing_headings_is_error(project: Path) -> None:
    for name in ("current-state.md", "documentation.md", "architecture-backlog.md"):
        _write(project / "project-context/0.review" / name)
    _write(project / "project-context/1.define/sad.md")
    result = validate_project(project, phase="review")
    assert not result.ok
    assert any("Proposed Enhancements" in i.message for i in result.issues)


def test_auto_uses_review_when_prd_missing(project: Path) -> None:
    _write_review_artifacts(project, status="pending")
    result = validate_project(project, phase="auto")
    assert result.ok, format_report(result)


def test_brownfield_define_requires_approval_and_prd(project: Path) -> None:
    _write_review_artifacts(project, status="pending")
    (project / "aamad.config.yml").write_text(
        "version: 1\nproject:\n  mode: brownfield\n", encoding="utf-8"
    )
    result = validate_project(project, phase="define")
    assert not result.ok
    assert any("Operator Decision" in i.message for i in result.issues)
    assert any(i.path.endswith("prd.md") for i in result.issues if i.level == "error")


def test_brownfield_define_passes_when_approved(project: Path) -> None:
    _write_review_artifacts(project, status="approved")
    _write(project / "project-context/1.define/prd.md")
    (project / "aamad.config.yml").write_text(
        "version: 1\nproject:\n  mode: brownfield\n", encoding="utf-8"
    )
    result = validate_project(project, phase="define")
    assert result.ok, format_report(result)
    assert not any(i.path.endswith("mrd.md") for i in result.issues)


def test_ux_review_missing_warns_when_ui_in_scope(project: Path) -> None:
    _write(project / "project-context/1.define/prd.md")
    _write(project / "project-context/1.define/sad.md")
    _write(
        project / "project-context/1.define/ux.md",
        "# UX\n\n**Approval status**: `approved`\n\n" + TERMINAL,
    )
    for name in ("setup.md", "frontend.md", "backend.md", "integration.md", "qa.md"):
        _write(project / "project-context/2.build" / name)
    result = validate_project(project, phase="build")
    assert result.ok, format_report(result)
    assert any(
        i.level == "warning" and i.path.endswith("ux-review.md") for i in result.issues
    )


def test_ux_review_missing_does_not_warn_on_no_ui_skip(project: Path) -> None:
    _write(project / "project-context/1.define/prd.md")
    _write(project / "project-context/1.define/sad.md")
    _write(
        project / "project-context/2.build/frontend.md",
        "# Frontend\n\n## Assumptions\n- no-UI skip: API-only service\n\n" + TERMINAL,
    )
    for name in ("setup.md", "backend.md", "integration.md", "qa.md"):
        _write(project / "project-context/2.build" / name)
    result = validate_project(project, phase="build")
    assert result.ok, format_report(result)
    assert not any(i.path.endswith("ux-review.md") for i in result.issues)


def test_ux_approval_pending_is_warning_not_error(project: Path) -> None:
    _write(project / "project-context/1.define/prd.md")
    _write(project / "project-context/1.define/sad.md")
    _write(
        project / "project-context/1.define/ux.md",
        "# UX\n\n**Approval status**: `pending`\n\n" + TERMINAL,
    )
    result = validate_project(project, phase="define")
    assert result.ok, format_report(result)
    assert any(
        i.level == "warning" and i.path.endswith("ux.md") and "pending" in i.message
        for i in result.issues
    )


def test_require_visual_regression_warns_without_evidence(project: Path) -> None:
    _write(project / "project-context/1.define/prd.md")
    _write(project / "project-context/1.define/sad.md")
    _write(
        project / "project-context/1.define/ux.md",
        "# UX\n\n**Approval status**: `approved`\n\n" + TERMINAL,
    )
    for name in ("setup.md", "frontend.md", "backend.md", "integration.md", "qa.md"):
        _write(project / "project-context/2.build" / name)
    _write(project / "project-context/2.build/ux-review.md")
    (project / "aamad.config.yml").write_text(
        "version: 1\ntesting:\n  require_visual_regression: true\n",
        encoding="utf-8",
    )
    result = validate_project(project, phase="build")
    assert result.ok, format_report(result)
    assert any(
        i.level == "warning"
        and i.path.endswith("ux-review.md")
        and "require_visual_regression" in i.message
        for i in result.issues
    )


def test_require_visual_regression_passes_with_evidence(project: Path) -> None:
    _write(project / "project-context/1.define/prd.md")
    _write(project / "project-context/1.define/sad.md")
    _write(
        project / "project-context/1.define/ux.md",
        "# UX\n\n**Approval status**: `approved`\n\n" + TERMINAL,
    )
    for name in ("setup.md", "frontend.md", "backend.md", "integration.md", "qa.md"):
        _write(project / "project-context/2.build" / name)
    _write(
        project / "project-context/2.build/ux-review.md",
        "# Review\n\n### 3b. Visual regression\n- Result: passed\n\n" + TERMINAL,
    )
    (project / "aamad.config.yml").write_text(
        "version: 1\ntesting:\n  require_visual_regression: true\n",
        encoding="utf-8",
    )
    result = validate_project(project, phase="build")
    assert result.ok, format_report(result)
    assert not any("require_visual_regression" in i.message for i in result.issues)


def test_brownfield_define_rejects_rejected_status(project: Path) -> None:
    _write_review_artifacts(project, status="rejected")
    _write(project / "project-context/1.define/prd.md")
    (project / "aamad.config.yml").write_text(
        "version: 1\nproject:\n  mode: brownfield\n", encoding="utf-8"
    )
    result = validate_project(project, phase="define")
    assert not result.ok
    assert any("rejected" in i.message for i in result.issues)
