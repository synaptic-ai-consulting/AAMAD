from __future__ import annotations

import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Iterable, Iterator

from .kiro import get_kiro_planned_paths, install_kiro

BUNDLE_CURSOR = "data/aamad_bundle.zip"
BUNDLE_CLAUDE = "data/aamad_claude_bundle.zip"

IDE_BUNDLES = {
    "cursor": BUNDLE_CURSOR,
    "claude-code": BUNDLE_CLAUDE,
    "claude_code": BUNDLE_CLAUDE,  # alias
    "vscode": BUNDLE_CURSOR,  # transform from Cursor bundle
    "kiro": BUNDLE_CURSOR,  # transform from Cursor bundle
}

KIRO_SHARED_FILES = (
    "CHECKLIST.md",
    "README.md",
    "aamad.config.example.yml",
)
KIRO_SHARED_DIRS = (
    "project-context",
    ".cursor/templates",
)

AGENTS_MD_TEMPLATE = """# AAMAD Agent Framework

This project uses the AAMAD framework for multi-agent development.
Framework version: {version}
See the full agent definitions in the IDE-specific directories.

## Agent Personas
- **@product-mgr** — Product Manager: Orchestrates product vision and requirements
- **@system.arch** — System Architect: Produces SAD and SFS documents
- **@project.mgr** — Project Manager: Scaffolds project and environment
- **@frontend.eng** — Frontend Developer: Builds MVP chat interface
- **@backend.eng** — Backend Developer: Builds backend for the selected runtime
- **@integration.eng** — Integration Engineer: Connects frontend and backend
- **@qa.eng** — QA Engineer: Validates MVP functionality (unit + integration)
- **@security.eng** — Security Engineer: Assesses MVP security before Deliver
- **@devops.eng** — DevOps Engineer: Packages deploy/CI, runbook, and user guide

## Workflow
1. **Define** (Phase 1): @product-mgr → elicitation → Market Research (optional) → PRD → @system.arch → SAD
2. **Build** (Phase 2): @project.mgr → @frontend.eng / @backend.eng → @integration.eng → @qa.eng → @security.eng
3. **Deliver** (Phase 3): @devops.eng → deploy.md + user-guide.md

## Rules
All development follows AAMAD core rules. See project-context/ for artifacts.
Run `aamad validate` to check artifact quality gates.

## Agent Definitions
{agents_dir_note}
"""


def _framework_version() -> str:
    try:
        from importlib import metadata

        return metadata.version("aamad")
    except Exception:  # pragma: no cover - local editable without metadata
        return "0.0.0"


def get_bundle_path(ide: str = "cursor") -> Path:
    """Return a filesystem path to the embedded artifact bundle for the given IDE."""
    bundle_name = IDE_BUNDLES.get(ide, IDE_BUNDLES["cursor"])
    with resources.as_file(resources.files("aamad") / bundle_name) as bundle:
        return bundle


def _agents_dir_note(ide: str) -> str:
    """Return the IDE-specific pointer for agent definitions."""
    if ide in ("claude-code", "claude_code"):
        return "See `.claude/agents/` for Claude Code agent definitions."
    if ide == "vscode":
        return "See `.github/agents/` for VS Code / GitHub Copilot agent definitions."
    if ide == "kiro":
        return "See `.kiro/agents/` for Kiro agent definitions."
    return "See `.cursor/agents/` for Cursor agent definitions."


def write_agents_md(
    destination: Path | str,
    *,
    ide: str = "cursor",
    overwrite: bool = False,
    dry_run: bool = False,
) -> Path | None:
    """
    Write AGENTS.md bridge file to the project root.

    This file is detected by VS Code + Copilot and can be read by Claude Code
    as a universal "README for agents".

    Returns:
        Path to AGENTS.md (created or would-be when dry_run).
    """
    dest = Path(destination).expanduser().resolve()
    path = dest / "AGENTS.md"
    if dry_run:
        return path
    if not overwrite and path.exists():
        raise FileExistsError(
            f"{path} already exists. Use overwrite=True to replace it."
        )
    content = AGENTS_MD_TEMPLATE.format(
        agents_dir_note=_agents_dir_note(ide),
        version=_framework_version(),
    )
    path.write_text(content, encoding="utf-8")
    return path


def extract_artifacts(
    destination: Path | str,
    *,
    ide: str = "cursor",
    overwrite: bool = False,
    dry_run: bool = False,
) -> list[Path]:
    """
    Extract the bundled artifacts into ``destination``.

    Also writes AGENTS.md (bridge file for IDE discoverability).
    For ide "vscode", extracts the Cursor bundle then runs VS Code conversion
    to produce .github/ and .vscode/ (Option A: transform on the fly).
    For ide "kiro", stages the Cursor bundle in a temp directory, converts
    to .kiro/, and copies only shared paths (templates, project-context, docs).

    Args:
        destination: Directory that should receive `.cursor/` or `.claude/` or `.github/` or `.kiro/`, `project-context/`, etc.
        ide: Target IDE — "cursor" (default), "claude-code", "vscode", or "kiro".
        overwrite: If False, raises FileExistsError when target already exists.
        dry_run: When True, no files are written; returns the would-be paths.
    """
    dest = Path(destination).expanduser().resolve()

    if ide == "kiro":
        return _extract_kiro(dest, overwrite=overwrite, dry_run=dry_run)

    installer = ArtifactInstaller(get_bundle_path(ide))
    paths = list(installer.extract(dest, overwrite=overwrite, dry_run=dry_run))

    if ide == "vscode":
        if dry_run:
            from aamad.vscode_copilot import get_vscode_planned_paths

            paths.extend(get_vscode_planned_paths(dest))
        else:
            from aamad.vscode_copilot import install_vscode_copilot

            paths.extend(install_vscode_copilot(dest, dest, overwrite=overwrite))

    # Add AGENTS.md (generated, not from bundle)
    agents_path = write_agents_md(
        destination,
        ide=ide,
        overwrite=overwrite,
        dry_run=dry_run,
    )
    if agents_path is not None:
        paths.append(agents_path)
    return paths


def _is_kiro_shared_member(filename: str) -> bool:
    normalized = filename.replace("\\", "/")
    if normalized in KIRO_SHARED_FILES:
        return True
    for prefix in KIRO_SHARED_DIRS:
        if normalized == prefix or normalized.startswith(prefix + "/"):
            return True
    return False


def _copy_kiro_shared(stage: Path, dest: Path, *, overwrite: bool) -> list[Path]:
    """Copy project-context, .cursor/templates, and root docs from a staged Cursor extract."""
    created: list[Path] = []
    for name in (*KIRO_SHARED_FILES, *KIRO_SHARED_DIRS):
        src = stage / name
        if not src.exists():
            continue
        target = dest / name
        if src.is_file():
            if target.exists() and not overwrite:
                raise FileExistsError(
                    f"{target} already exists. Use overwrite=True to replace it."
                )
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)
            created.append(target)
            continue
        for file_path in sorted(src.rglob("*")):
            if file_path.is_dir():
                continue
            rel = file_path.relative_to(src)
            out_path = target / rel
            if out_path.exists() and not overwrite:
                raise FileExistsError(
                    f"{out_path} already exists. Use overwrite=True to replace it."
                )
            out_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, out_path)
            created.append(out_path)
    return created


def _extract_kiro(
    dest: Path,
    *,
    overwrite: bool,
    dry_run: bool,
) -> list[Path]:
    """Stage the Cursor bundle, convert to .kiro/, and copy shared artifacts."""
    installer = ArtifactInstaller(get_bundle_path("cursor"))
    shared_paths = [
        dest / name
        for name in installer.preview()
        if _is_kiro_shared_member(name) and not name.endswith("/")
    ]
    kiro_paths = get_kiro_planned_paths(dest)
    skill_paths = []
    for name in installer.preview():
        normalized = name.replace("\\", "/")
        if normalized.startswith(".cursor/skills/") and not normalized.endswith("/"):
            rel = normalized[len(".cursor/skills/") :]
            skill_paths.append(dest / ".kiro" / "skills" / rel)

    if dry_run:
        agents_path = write_agents_md(dest, ide="kiro", overwrite=overwrite, dry_run=True)
        paths = shared_paths + kiro_paths + skill_paths
        if agents_path is not None:
            paths.append(agents_path)
        return paths

    with tempfile.TemporaryDirectory() as tmp:
        stage = Path(tmp)
        installer.extract(stage, overwrite=True, dry_run=False)
        created = list(install_kiro(stage, dest, overwrite=overwrite))
        created.extend(_copy_kiro_shared(stage, dest, overwrite=overwrite))

    agents_path = write_agents_md(dest, ide="kiro", overwrite=overwrite, dry_run=False)
    if agents_path is not None:
        created.append(agents_path)
    return created


@dataclass
class ArtifactInstaller:
    """Utility object that manages the bundled zip file."""

    bundle_path: Path

    def iter_members(self) -> Iterator[zipfile.ZipInfo]:
        with zipfile.ZipFile(self.bundle_path, "r") as zf:
            for member in zf.infolist():
                yield member

    def preview(self) -> list[str]:
        return [m.filename for m in self.iter_members()]

    def extract(
        self,
        destination: Path,
        *,
        overwrite: bool = False,
        dry_run: bool = False,
    ) -> list[Path]:
        destination = destination.expanduser().resolve()
        if dry_run:
            return self._planned_paths(destination)

        with zipfile.ZipFile(self.bundle_path, "r") as zf:
            for member in zf.infolist():
                target = destination / member.filename
                if member.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                if not overwrite and target.exists():
                    raise FileExistsError(
                        f"{target} already exists. Use overwrite=True to replace it."
                    )
                target.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(member, "r") as src, open(target, "wb") as dst:
                    shutil.copyfileobj(src, dst)
        return self._planned_paths(destination)

    def _planned_paths(self, destination: Path) -> list[Path]:
        members: Iterable[str] = [m.filename for m in self.iter_members()]
        return [destination / name for name in members]
