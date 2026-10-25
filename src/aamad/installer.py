from __future__ import annotations

import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Iterable, Iterator

import yaml

from .kiro import get_kiro_planned_paths, install_kiro
from .vscode_copilot import get_vscode_planned_paths, install_vscode_copilot

BUNDLE_CURSOR = "data/aamad_bundle.zip"
BUNDLE_CLAUDE = "data/aamad_claude_bundle.zip"

IDE_BUNDLES = {
    "cursor": BUNDLE_CURSOR,
    "claude-code": BUNDLE_CLAUDE,
    "claude_code": BUNDLE_CLAUDE,  # alias
    "vscode": BUNDLE_CURSOR,  # transform from Cursor bundle
    "kiro": BUNDLE_CURSOR,  # transform from Cursor bundle
}

SHARED_FILES = (
    "CHECKLIST.md",
    "README.md",
    "aamad.config.example.yml",
    "NOTICES",
)
SHARED_DIRS = ("project-context",)

AGENTS_MD_TEMPLATE = """# AAMAD Agent Framework

This project uses the AAMAD framework for multi-agent development.
Framework version: {version}
See the full agent definitions in the IDE-specific directories.

## Agent Personas
- **@product-mgr** — Product Manager: Orchestrates product vision and requirements
- **@system.arch** — System Architect: Reviews existing code (brownfield) and produces SAD/SFS
- **@ux.designer** — UX Designer: Interaction design and visual direction (`ux.md`)
- **@project.mgr** — Project Manager: Scaffolds project and environment
- **@frontend.eng** — Frontend Developer: Implements the approved MVP UI
- **@backend.eng** — Backend Developer: Builds backend for the selected runtime
- **@integration.eng** — Integration Engineer: Connects frontend and backend
- **@qa.eng** — QA Engineer: Validates MVP functionality (unit + integration)
- **@security.eng** — Security Engineer: Assesses MVP security before Deliver
- **@devops.eng** — DevOps Engineer: Packages deploy/CI, runbook, and user guide

## Workflow
Greenfield (default, `project.mode: greenfield`):
1. **Define** (Phase 1): @product-mgr → elicitation → Market Research (optional) → PRD → @system.arch → SAD → @ux.designer → ux.md (when UI is in scope)
2. **Build** (Phase 2): @project.mgr → @frontend.eng / @backend.eng → @integration.eng → @qa.eng → @security.eng
3. **Deliver** (Phase 3): @devops.eng → deploy.md + user-guide.md

Brownfield (`project.mode: brownfield`):
1. **Review** (Phase 0): @system.arch → *review-codebase → *create-sad (as-is + proposed enhancements) → operator decision
2. **Constrained Define** (Phase 1): @product-mgr writes PRD and stories only for approved enhancements
3. **UX** (material UI enhancements only): @ux.designer → enhancement-scoped ux.md
4. **Build** then **Deliver** as above; extend the existing tree — do not scaffold a replacement app

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


def _skip_if_exists(dest: Path, *, mode: str, overwrite: bool) -> frozenset[str]:
    """Bundle members to leave in place for brownfield init."""
    if mode == "brownfield" and not overwrite and (dest / "README.md").is_file():
        return frozenset({"README.md"})
    return frozenset()


def _merge_project_mode(path: Path, mode: str, runtime: str | None = None) -> None:
    """Create or merge ``project.mode`` (and optional runtime) without clobbering other keys."""
    data: dict = {}
    if path.is_file():
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            data = loaded
    if "version" not in data:
        data["version"] = 2
    project = data.get("project")
    if not isinstance(project, dict):
        project = {}
    project["mode"] = mode
    data["project"] = project
    if runtime and runtime != "later":
        runtime_block = data.get("runtime")
        if not isinstance(runtime_block, dict):
            runtime_block = {}
        runtime_block["target"] = runtime
        data["runtime"] = runtime_block
    path.write_text(
        yaml.safe_dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def _merge_dotenv(path: Path, key: str, value: str) -> None:
    """Set ``key=value`` in a dotenv file, replacing a prior assignment of the same key."""
    lines: list[str] = []
    if path.is_file():
        lines = path.read_text(encoding="utf-8").splitlines()
    updated: list[str] = []
    found = False
    prefix = f"{key}="
    export_prefix = f"export {key}="
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(prefix) or stripped.startswith(export_prefix):
            updated.append(f"{key}={value}")
            found = True
        else:
            updated.append(line)
    if not found:
        if updated and updated[-1] != "":
            updated.append("")
        updated.append(f"{key}={value}")
    path.write_text("\n".join(updated) + "\n", encoding="utf-8")


def _set_claude_runtime(dest: Path, runtime: str) -> Path | None:
    """Update ``AAMAD_TARGET_RUNTIME`` in ``.claude/settings.json`` when present."""
    import json

    settings_path = dest / ".claude" / "settings.json"
    if not settings_path.is_file():
        return None
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        data = {}
    if not isinstance(data, dict):
        data = {}
    env = data.get("env")
    if not isinstance(env, dict):
        env = {}
    env["AAMAD_TARGET_RUNTIME"] = runtime
    data["env"] = env
    settings_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return settings_path


def write_mode_artifacts(
    destination: Path,
    *,
    mode: str,
    runtime: str | None = None,
    dry_run: bool = False,
) -> list[Path]:
    """Write ``aamad.config.yml`` project.mode, optional runtime, and brownfield placeholder."""
    dest = Path(destination).expanduser().resolve()
    created: list[Path] = []
    config_path = dest / "aamad.config.yml"
    created.append(config_path)
    env_path = dest / ".env"
    apply_runtime = bool(runtime and runtime != "later")
    if apply_runtime:
        created.append(env_path)
    if not dry_run:
        _merge_project_mode(config_path, mode, runtime)
        if apply_runtime:
            _merge_dotenv(env_path, "AAMAD_TARGET_RUNTIME", runtime)
            _set_claude_runtime(dest, runtime)
    if mode == "brownfield":
        gitkeep = dest / "project-context" / "0.review" / ".gitkeep"
        created.append(gitkeep)
        if not dry_run:
            gitkeep.parent.mkdir(parents=True, exist_ok=True)
            if not gitkeep.exists():
                gitkeep.write_text("", encoding="utf-8")
    return created


def extract_artifacts(
    destination: Path | str,
    *,
    ide: str = "cursor",
    mode: str = "greenfield",
    runtime: str | None = None,
    overwrite: bool = False,
    dry_run: bool = False,
) -> list[Path]:
    """
    Extract the bundled artifacts into ``destination``.

    Also writes AGENTS.md (bridge file for IDE discoverability) and merges
    ``project.mode`` into ``aamad.config.yml``.
    For ide "vscode" and "kiro", stages the Cursor bundle in a temp directory,
    converts into `.github/` / `.kiro/`, and copies only shared paths
    (`project-context/`, docs). Templates land in the IDE folder.

    Args:
        destination: Directory that should receive `.cursor/` or `.claude/` or `.github/` or `.kiro/`, `project-context/`, etc.
        ide: Target IDE — "cursor" (default), "claude-code", "vscode", or "kiro".
        mode: Project spine — "greenfield" (default) or "brownfield".
        runtime: Greenfield runtime adapter — ``crewai``, ``claude-agent-sdk``,
            ``cursor-sdk``, or ``later`` / ``None`` (do not set the variable).
        overwrite: If False, raises FileExistsError when target already exists.
        dry_run: When True, no files are written; returns the would-be paths.
    """
    dest = Path(destination).expanduser().resolve()
    skip = _skip_if_exists(dest, mode=mode, overwrite=overwrite)

    if ide == "kiro":
        return _extract_from_cursor_stage(
            dest,
            ide="kiro",
            mode=mode,
            runtime=runtime,
            overwrite=overwrite,
            dry_run=dry_run,
            skip_if_exists=skip,
            install=install_kiro,
            planned_paths=get_kiro_planned_paths(dest),
            extra_mapped_prefixes=((".cursor/skills/", ".kiro/skills/"),),
        )
    if ide == "vscode":
        return _extract_from_cursor_stage(
            dest,
            ide="vscode",
            mode=mode,
            runtime=runtime,
            overwrite=overwrite,
            dry_run=dry_run,
            skip_if_exists=skip,
            install=install_vscode_copilot,
            planned_paths=get_vscode_planned_paths(dest),
            extra_mapped_prefixes=((".cursor/skills/", ".github/skills/"),),
        )

    installer = ArtifactInstaller(get_bundle_path(ide))
    paths = list(
        installer.extract(
            dest,
            overwrite=overwrite,
            dry_run=dry_run,
            skip_if_exists=skip,
        )
    )

    agents_path = write_agents_md(
        destination,
        ide=ide,
        overwrite=overwrite,
        dry_run=dry_run,
    )
    if agents_path is not None:
        paths.append(agents_path)
    paths.extend(write_mode_artifacts(dest, mode=mode, runtime=runtime, dry_run=dry_run))
    return paths


def _is_shared_member(filename: str) -> bool:
    normalized = filename.replace("\\", "/")
    if normalized in SHARED_FILES:
        return True
    for prefix in SHARED_DIRS:
        if normalized == prefix or normalized.startswith(prefix + "/"):
            return True
    return False


def _copy_shared(
    stage: Path,
    dest: Path,
    *,
    overwrite: bool,
    skip_if_exists: frozenset[str] = frozenset(),
) -> list[Path]:
    """Copy project-context and root docs from a staged Cursor extract."""
    created: list[Path] = []
    for name in (*SHARED_FILES, *SHARED_DIRS):
        src = stage / name
        if not src.exists():
            continue
        target = dest / name
        if src.is_file():
            if target.exists() and name in skip_if_exists:
                continue
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


def _extract_from_cursor_stage(
    dest: Path,
    *,
    ide: str,
    mode: str,
    runtime: str | None = None,
    overwrite: bool,
    dry_run: bool,
    skip_if_exists: frozenset[str],
    install,
    planned_paths: list[Path],
    extra_mapped_prefixes: tuple[tuple[str, str], ...] = (),
) -> list[Path]:
    """Stage the Cursor bundle, convert to an IDE tree, and copy shared artifacts."""
    installer = ArtifactInstaller(get_bundle_path("cursor"))
    shared_paths = [
        dest / name
        for name in installer.preview()
        if _is_shared_member(name)
        and not name.endswith("/")
        and name.replace("\\", "/") not in skip_if_exists
    ]
    mapped_paths: list[Path] = []
    for name in installer.preview():
        normalized = name.replace("\\", "/")
        if normalized.endswith("/"):
            continue
        for src_prefix, dest_prefix in extra_mapped_prefixes:
            if normalized.startswith(src_prefix):
                rel = normalized[len(src_prefix) :]
                mapped_paths.append(dest / dest_prefix / rel)

    if dry_run:
        agents_path = write_agents_md(dest, ide=ide, overwrite=overwrite, dry_run=True)
        paths = shared_paths + list(planned_paths) + mapped_paths
        if agents_path is not None:
            paths.append(agents_path)
        paths.extend(write_mode_artifacts(dest, mode=mode, runtime=runtime, dry_run=True))
        return paths

    with tempfile.TemporaryDirectory() as tmp:
        stage = Path(tmp)
        installer.extract(stage, overwrite=True, dry_run=False)
        created = list(install(stage, dest, overwrite=overwrite))
        created.extend(
            _copy_shared(
                stage,
                dest,
                overwrite=overwrite,
                skip_if_exists=skip_if_exists,
            )
        )

    agents_path = write_agents_md(dest, ide=ide, overwrite=overwrite, dry_run=False)
    if agents_path is not None:
        created.append(agents_path)
    created.extend(write_mode_artifacts(dest, mode=mode, runtime=runtime, dry_run=False))
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
        skip_if_exists: frozenset[str] = frozenset(),
    ) -> list[Path]:
        destination = destination.expanduser().resolve()
        if dry_run:
            return self._planned_paths(destination, skip_if_exists=skip_if_exists)

        with zipfile.ZipFile(self.bundle_path, "r") as zf:
            for member in zf.infolist():
                normalized = member.filename.replace("\\", "/").rstrip("/")
                target = destination / member.filename
                if member.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                if normalized in skip_if_exists and target.exists():
                    continue
                if not overwrite and target.exists():
                    raise FileExistsError(
                        f"{target} already exists. Use overwrite=True to replace it."
                    )
                target.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(member, "r") as src, open(target, "wb") as dst:
                    shutil.copyfileobj(src, dst)
        return self._planned_paths(destination, skip_if_exists=skip_if_exists)

    def _planned_paths(
        self,
        destination: Path,
        *,
        skip_if_exists: frozenset[str] = frozenset(),
    ) -> list[Path]:
        members: Iterable[str] = [m.filename for m in self.iter_members()]
        paths: list[Path] = []
        for name in members:
            normalized = name.replace("\\", "/").rstrip("/")
            if normalized in skip_if_exists and (destination / name).exists():
                continue
            paths.append(destination / name)
        return paths
