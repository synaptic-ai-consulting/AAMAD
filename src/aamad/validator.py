"""Validate AAMAD project-context artifacts against framework quality gates."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

REQUIRED_TERMINAL_HEADINGS = (
    "## Sources",
    "## Assumptions",
    "## Open Questions",
    "## Audit",
)

# Artifacts expected after each phase gate (relative to project root).
DEFINE_REQUIRED = (
    "project-context/1.define/prd.md",
    "project-context/1.define/sad.md",
)
DEFINE_OPTIONAL = (
    "project-context/1.define/mrd.md",
)
REVIEW_ARTIFACTS = (
    "project-context/0.review/current-state.md",
    "project-context/0.review/documentation.md",
    "project-context/0.review/architecture-backlog.md",
)
REVIEW_REQUIRED = REVIEW_ARTIFACTS + ("project-context/1.define/sad.md",)
REVIEW_SAD_HEADINGS = (
    "Proposed Enhancements",
    "Operator Decision",
)
SAD_DECISION_HEADINGS = (
    "Work Ownership",
    "Pattern Decision",
    "Reference Architecture",
    "Model and Context Strategy",
    "Control Register",
)
EVALS_MD = "project-context/2.build/evals.md"
SECURITY_MD = "project-context/2.build/security.md"
PRIMARY_SHAPE_RE = re.compile(
    r"(?i)primary shape\*?\*?\s*[:=]\s*`?(augmented call|workflow|agent|none|n/?a|no model)"
)
NO_MODEL_SHAPES = frozenset({"none", "n/a", "na", "no model"})
AGENT_TURN_BUDGET_RE = re.compile(r"(?i)turn budget")
AGENT_STOP_RE = re.compile(r"(?i)stop condition")
BUILD_ARTIFACTS = (
    "project-context/2.build/setup.md",
    "project-context/2.build/frontend.md",
    "project-context/2.build/backend.md",
    "project-context/2.build/integration.md",
    "project-context/2.build/qa.md",
)
# Optional Build artifact: warning-only so projects that upgrade mid-build or
# were built before this capability existed do not fail the build/deliver gate.
BUILD_OPTIONAL = (
    "project-context/2.build/evals.md",
)
UX_SPEC = "project-context/1.define/ux.md"
UX_REVIEW = "project-context/2.build/ux-review.md"
FRONTEND_MD = "project-context/2.build/frontend.md"
DELIVER_ARTIFACTS = (
    "project-context/3.deliver/deploy.md",
)

RUNTIME_AUDIT_RE = re.compile(
    r"AAMAD_TARGET_RUNTIME\s*[:=]\s*`?(crewai|claude-agent-sdk|cursor-sdk)`?",
    re.IGNORECASE,
)

OPERATOR_STATUS_RE = re.compile(
    r"(?i)(?:status|decision)\s*[:=]\s*`?(pending|approved-with-changes|approved|rejected)`?"
)
OPERATOR_STATUS_WORD_RE = re.compile(
    r"(?i)\b(pending|approved-with-changes|approved|rejected)\b"
)
APPROVED_STATUSES = frozenset({"approved", "approved-with-changes"})

NO_UI_SKIP_RE = re.compile(
    r"(?i)\bno[- ]ui skip\b|\bno user-facing UI\b|\bno user facing UI\b"
)
UX_APPROVAL_RE = re.compile(
    r"(?i)(?:approval status|\*\*approval status\*\*|approval)\s*[:=]\s*`?"
    r"(pending|approved-with-changes|approved|rejected)`?"
)
VISUAL_PASSED_OR_FAILED_RE = re.compile(
    r"(?i)visual regression[\s\S]{0,800}\b(passed|failed)\b"
)
VISUAL_NOT_TESTED_RE = re.compile(
    r"(?i)visual regression[\s\S]{0,800}\bnot tested\b"
)
VISUAL_SKIP_RE = re.compile(
    r"(?i)(no[- ]ui skip|no user-facing UI|no user facing UI|skip rationale|"
    r"operator declined|brownfield small change)"
)

KNOWN_CONFIG_TOP_KEYS = frozenset(
    {
        "version",
        "project",
        "runtime",
        "language",
        "libraries",
        "ui",
        "coding_standards",
        "security",
        "documentation",
        "testing",
        "model",
        "spend",
        "crew",
        "quality",
    }
)


@dataclass
class ValidationIssue:
    level: str  # "error" | "warning"
    path: str
    message: str


@dataclass
class ValidationResult:
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(i.level == "error" for i in self.issues)

    def add(self, level: str, path: str, message: str) -> None:
        self.issues.append(ValidationIssue(level=level, path=path, message=message))


def _heading_present(text: str, heading: str) -> bool:
    """True if heading appears as a markdown heading (## or ###)."""
    pattern = re.compile(
        rf"^#{{2,3}}\s+{re.escape(heading.lstrip('#').strip())}\s*$",
        re.MULTILINE | re.IGNORECASE,
    )
    return bool(pattern.search(text))


def _check_terminal_sections(path: Path, result: ValidationResult) -> None:
    text = path.read_text(encoding="utf-8")
    rel = str(path)
    for heading in REQUIRED_TERMINAL_HEADINGS:
        label = heading.lstrip("#").strip()
        if not _heading_present(text, label):
            result.add("error", rel, f"Missing required heading: {heading}")


def _check_runtime_in_audit(path: Path, result: ValidationResult, *, required: bool) -> None:
    text = path.read_text(encoding="utf-8")
    rel = str(path)
    # Prefer Audit section if present
    audit_match = re.search(
        r"^##\s+Audit\s*$(.*)",
        text,
        re.MULTILINE | re.IGNORECASE | re.DOTALL,
    )
    scope = audit_match.group(1) if audit_match else text
    if RUNTIME_AUDIT_RE.search(scope):
        return
    level = "error" if required else "warning"
    result.add(
        level,
        rel,
        "Audit should record resolved AAMAD_TARGET_RUNTIME "
        "(crewai | claude-agent-sdk | cursor-sdk)",
    )


def _operator_decision_status(text: str) -> str | None:
    """Return the Operator Decision status if the section exists."""
    match = re.search(
        r"^#{2,3}\s+Operator Decision\s*$(.*?)(?=^#{2,3}\s|\Z)",
        text,
        re.MULTILINE | re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return None
    section = match.group(1)
    status_match = OPERATOR_STATUS_RE.search(section)
    if status_match:
        return status_match.group(1).lower()
    word = OPERATOR_STATUS_WORD_RE.search(section)
    return word.group(1).lower() if word else None


def _read_config(root: Path) -> dict:
    path = root / "aamad.config.yml"
    if not path.is_file():
        return {}
    try:
        import yaml

        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _read_project_mode(root: Path) -> str | None:
    project = _read_config(root).get("project")
    if not isinstance(project, dict):
        return None
    mode = project.get("mode")
    if mode in ("greenfield", "brownfield"):
        return mode
    return None


def _config_flag(root: Path, section: str, key: str, default: bool) -> bool:
    data = _read_config(root).get(section)
    if not isinstance(data, dict) or key not in data:
        return default
    return bool(data.get(key))


def _require_evals(root: Path) -> bool:
    return _config_flag(root, "quality", "require_evals", True)


def _require_security_assessment(root: Path) -> bool:
    return _config_flag(root, "security", "require_security_assessment", True)


def _section_body(text: str, heading: str) -> str | None:
    match = re.search(
        rf"^#{{2,3}}\s+{re.escape(heading)}\s*$(.*?)(?=^#{{2,3}}\s|\Z)",
        text,
        re.MULTILINE | re.IGNORECASE | re.DOTALL,
    )
    return match.group(1) if match else None


def _primary_shape(text: str) -> str | None:
    section = _section_body(text, "Pattern Decision") or text
    match = PRIMARY_SHAPE_RE.search(section)
    return match.group(1).lower() if match else None


def _pattern_includes_model_call(text: str) -> bool:
    shape = _primary_shape(text)
    if shape is None:
        return True
    return shape not in NO_MODEL_SHAPES


def _check_sad_decision_headings(path: Path, result: ValidationResult) -> None:
    text = path.read_text(encoding="utf-8")
    rel = str(path)
    for heading in SAD_DECISION_HEADINGS:
        if not _heading_present(text, heading):
            result.add("error", rel, f"Missing required heading: {heading}")
    shape = _primary_shape(text)
    if shape != "agent":
        return
    section = _section_body(text, "Pattern Decision") or text
    if not AGENT_TURN_BUDGET_RE.search(section):
        result.add(
            "error",
            rel,
            "Agent Pattern Decision must record a turn budget",
        )
    if not AGENT_STOP_RE.search(section):
        result.add(
            "error",
            rel,
            "Agent Pattern Decision must record stop conditions",
        )


def _require_visual_regression(root: Path) -> bool:
    testing = _read_config(root).get("testing")
    if not isinstance(testing, dict):
        return False
    return bool(testing.get("require_visual_regression"))


def _ui_in_scope(root: Path) -> bool:
    if (root / UX_SPEC).is_file():
        return True
    frontend = root / FRONTEND_MD
    if not frontend.is_file():
        return False
    return not NO_UI_SKIP_RE.search(frontend.read_text(encoding="utf-8"))


def _ux_approval_status(text: str) -> str | None:
    match = UX_APPROVAL_RE.search(text)
    return match.group(1).lower() if match else None


def _has_visual_regression_evidence(text: str) -> bool:
    if VISUAL_PASSED_OR_FAILED_RE.search(text):
        return True
    if VISUAL_NOT_TESTED_RE.search(text) and VISUAL_SKIP_RE.search(text):
        return True
    return False


def _check_ux_gates(root: Path, phase: str, result: ValidationResult) -> None:
    ux_path = root / UX_SPEC
    if ux_path.is_file() and phase in ("define", "build", "deliver"):
        _check_terminal_sections(ux_path, result)
        status = _ux_approval_status(ux_path.read_text(encoding="utf-8"))
        if status is None or status not in APPROVED_STATUSES:
            label = status if status else "missing"
            result.add(
                "warning",
                UX_SPEC,
                f"ux.md Approval status is {label}; "
                "material UI work expects approved or approved-with-changes",
            )

    if phase not in ("build", "deliver"):
        return
    if not _ui_in_scope(root):
        return

    review = root / UX_REVIEW
    if review.is_file():
        _check_terminal_sections(review, result)
    else:
        result.add(
            "warning",
            UX_REVIEW,
            "ux-review.md not found (recommended for UI projects; run *review-ui)",
        )

    if not _require_visual_regression(root):
        return
    review_text = review.read_text(encoding="utf-8") if review.is_file() else ""
    if not _has_visual_regression_evidence(review_text):
        result.add(
            "warning",
            UX_REVIEW,
            "testing.require_visual_regression is true but ux-review.md has no "
            "visual-regression evidence (passed / failed / not tested with skip rationale)",
        )


def _is_brownfield(root: Path, exists) -> bool:
    mode = _read_project_mode(root)
    if mode == "brownfield":
        return True
    if mode == "greenfield":
        return False
    return any(exists(p) for p in REVIEW_ARTIFACTS)


def _check_review_sad_headings(path: Path, result: ValidationResult) -> None:
    text = path.read_text(encoding="utf-8")
    rel = str(path)
    for heading in REVIEW_SAD_HEADINGS:
        if not _heading_present(text, heading):
            result.add("error", rel, f"Missing required heading: {heading}")


def _check_operator_decision(
    path: Path,
    result: ValidationResult,
    *,
    require_approved: bool,
) -> None:
    text = path.read_text(encoding="utf-8")
    rel = str(path)
    status = _operator_decision_status(text)
    if status is None:
        result.add(
            "error",
            rel,
            "Operator Decision section is missing a status "
            "(pending | approved | approved-with-changes | rejected)",
        )
        return
    if require_approved and status not in APPROVED_STATUSES:
        result.add(
            "error",
            rel,
            f"Operator Decision status is {status}; "
            "constrained Define requires approved or approved-with-changes",
        )


def validate_project(
    root: Path | str,
    *,
    phase: str = "auto",
) -> ValidationResult:
    """
    Validate project-context artifacts under ``root``.

    phase:
      - ``review``: require 0.review artifacts + sad.md (brownfield)
      - ``define``: require prd.md + sad.md; mrd.md optional (skipped for brownfield)
      - ``build``: define + build artifacts (qa.md required)
      - ``deliver``: build + deploy.md (qa.md gate)
      - ``auto``: validate whatever artifacts exist; enforce gates when later phases appear
    """
    root = Path(root).expanduser().resolve()
    result = ValidationResult()
    phase = phase.lower().strip()

    def exists(rel: str) -> bool:
        return (root / rel).is_file()

    deliver_present = exists(DELIVER_ARTIFACTS[0])
    build_present = any(exists(p) for p in BUILD_ARTIFACTS)
    qa_present = exists("project-context/2.build/qa.md")
    review_started = any(exists(p) for p in REVIEW_ARTIFACTS)
    prd_present = exists("project-context/1.define/prd.md")
    brownfield = _is_brownfield(root, exists)

    if phase == "auto":
        if deliver_present:
            phase = "deliver"
        elif build_present or qa_present:
            phase = "build"
        elif review_started and not prd_present:
            phase = "review"
        else:
            phase = "define"

    if phase == "review" or (brownfield and phase in ("define", "build", "deliver")):
        for rel in REVIEW_REQUIRED:
            path = root / rel
            if not path.is_file():
                result.add("error", rel, "Required Review artifact missing")
                continue
            _check_terminal_sections(path, result)
            if rel.endswith("sad.md"):
                _check_runtime_in_audit(path, result, required=True)
                _check_review_sad_headings(path, result)
                _check_operator_decision(
                    path,
                    result,
                    require_approved=phase in ("define", "build", "deliver"),
                )
                if phase in ("define", "build", "deliver"):
                    _check_sad_decision_headings(path, result)

    if phase in ("define", "build", "deliver"):
        for rel in DEFINE_REQUIRED:
            path = root / rel
            if not path.is_file():
                result.add("error", rel, "Required Define artifact missing")
                continue
            if brownfield and rel.endswith("sad.md"):
                continue
            _check_terminal_sections(path, result)
            if rel.endswith("sad.md"):
                _check_runtime_in_audit(path, result, required=True)
                _check_sad_decision_headings(path, result)

        for rel in DEFINE_OPTIONAL:
            path = root / rel
            if path.is_file():
                _check_terminal_sections(path, result)
            elif phase == "define" and not brownfield:
                result.add(
                    "warning",
                    rel,
                    "MRD not found (optional for internal/personal projects)",
                )

    if phase in ("build", "deliver"):
        for rel in BUILD_ARTIFACTS:
            path = root / rel
            if not path.is_file():
                # Only require qa.md hard; others warn if missing mid-build
                level = "error" if rel.endswith("qa.md") else "warning"
                result.add(level, rel, "Build artifact missing")
                continue
            _check_terminal_sections(path, result)
            if rel.endswith(("backend.md", "integration.md", "qa.md")):
                _check_runtime_in_audit(path, result, required=rel.endswith("backend.md"))

        for rel in BUILD_OPTIONAL:
            path = root / rel
            if path.is_file():
                _check_terminal_sections(path, result)
            else:
                if phase == "deliver" and _require_evals(root):
                    continue
                result.add(
                    "warning",
                    rel,
                    "evals.md not found (recommended before Deliver; run *run-evals)",
                )

    if phase == "deliver":
        if not qa_present:
            result.add(
                "error",
                "project-context/2.build/qa.md",
                "Deliver phase gate failed: qa.md must exist before deploy",
            )
        sad = root / "project-context/1.define/sad.md"
        sad_text = sad.read_text(encoding="utf-8") if sad.is_file() else ""
        evals = root / EVALS_MD
        if evals.is_file():
            _check_terminal_sections(evals, result)
        elif _require_evals(root) and _pattern_includes_model_call(sad_text):
            result.add(
                "error",
                EVALS_MD,
                "Deliver phase gate failed: evals.md required when the "
                "Pattern Decision includes a model call",
            )
        security = root / SECURITY_MD
        if security.is_file():
            _check_terminal_sections(security, result)
        elif _require_security_assessment(root):
            result.add(
                "error",
                SECURITY_MD,
                "Deliver phase gate failed: security.md required when "
                "security.require_security_assessment is true",
            )
        deploy = root / DELIVER_ARTIFACTS[0]
        if not deploy.is_file():
            result.add("error", DELIVER_ARTIFACTS[0], "Deliver artifact missing")
        else:
            _check_terminal_sections(deploy, result)
            _check_runtime_in_audit(deploy, result, required=True)
            if not _heading_present(deploy.read_text(encoding="utf-8"), "Outcome Document"):
                result.add(
                    "error",
                    DELIVER_ARTIFACTS[0],
                    "Missing required heading: Outcome Document",
                )

    _check_ux_gates(root, phase, result)
    _check_aamad_config(root, result)
    return result


def _check_aamad_config(root: Path, result: ValidationResult) -> None:
    """Validate aamad.config.yml when present (parse + known top-level keys)."""
    path = root / "aamad.config.yml"
    if not path.is_file():
        return
    rel = "aamad.config.yml"
    try:
        import yaml

        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - parse errors
        result.add("error", rel, f"Failed to parse YAML: {exc}")
        return
    if data is None:
        result.add("warning", rel, "Config file is empty")
        return
    if not isinstance(data, dict):
        result.add("error", rel, "Config root must be a mapping")
        return
    unknown = sorted(set(data.keys()) - KNOWN_CONFIG_TOP_KEYS)
    if unknown:
        result.add(
            "error",
            rel,
            f"Unknown top-level key(s): {', '.join(unknown)}",
        )


def format_report(result: ValidationResult) -> str:
    if not result.issues:
        return "OK: no validation issues found."
    lines = []
    for issue in result.issues:
        lines.append(f"[{issue.level.upper()}] {issue.path}: {issue.message}")
    summary = "PASSED" if result.ok else "FAILED"
    lines.append(f"\nValidation {summary} ({len(result.issues)} issue(s)).")
    return "\n".join(lines)
