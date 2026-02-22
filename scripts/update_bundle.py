"""
Utility script to rebuild the embedded artifact bundles for Cursor and Claude Code.

Usage:
    python scripts/update_bundle.py
"""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "src" / "aamad" / "data"

# Cursor bundle: .cursor/, project-context/, docs
CURSOR_BUNDLE = DATA_DIR / "aamad_bundle.zip"
CURSOR_INCLUDE = [".cursor", "project-context", "CHECKLIST.md", "README.md"]

# Claude Code bundle: .claude/, project-context/, .cursor/templates/, docs
CLAUDE_BUNDLE = DATA_DIR / "aamad_claude_bundle.zip"
CLAUDE_INCLUDE = [".claude", "project-context", ".cursor/templates", "CHECKLIST.md", "README.md"]


def _add_to_zip(zf: zipfile.ZipFile, root: Path, items: list[str]) -> None:
    """Add files/dirs from root to zip, preserving relative paths."""
    for name in items:
        path = root / name
        if not path.exists():
            continue
        if path.is_file():
            zf.write(path, arcname=path.name)
            continue
        for file in path.rglob("*"):
            if file.is_dir():
                continue
            rel = file.relative_to(root)
            zf.write(file, arcname=str(rel))


def build_cursor_bundle() -> None:
    """Build the Cursor-format bundle (aamad_bundle.zip)."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if CURSOR_BUNDLE.exists():
        CURSOR_BUNDLE.unlink()

    with zipfile.ZipFile(CURSOR_BUNDLE, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        _add_to_zip(zf, ROOT, CURSOR_INCLUDE)
    print(f"Updated Cursor bundle at {CURSOR_BUNDLE}")


def build_claude_bundle() -> None:
    """Build the Claude Code-format bundle (aamad_claude_bundle.zip)."""
    import sys
    sys.path.insert(0, str(ROOT / "src"))
    from aamad.claude_code import install_claude_code

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if CLAUDE_BUNDLE.exists():
        CLAUDE_BUNDLE.unlink()

    # Stage: run conversion to produce .claude/ in a temp dir
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        stage = Path(tmp)
        # Conversion needs .cursor/ as source; use repo root
        install_claude_code(ROOT, stage, overwrite=True)
        # Also copy project-context, .cursor/templates, docs (conversion only creates .claude/)
        for name in ["project-context", "CHECKLIST.md", "README.md"]:
            src = ROOT / name
            if src.exists():
                if src.is_file():
                    shutil.copy2(src, stage / name)
                else:
                    shutil.copytree(src, stage / name, dirs_exist_ok=True)
        # .cursor/templates (agents reference these)
        templates_src = ROOT / ".cursor" / "templates"
        if templates_src.exists():
            (stage / ".cursor" / "templates").parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(templates_src, stage / ".cursor" / "templates", dirs_exist_ok=True)

        with zipfile.ZipFile(CLAUDE_BUNDLE, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            _add_to_zip(zf, stage, [".claude", "project-context", ".cursor", "CHECKLIST.md", "README.md"])

    print(f"Updated Claude Code bundle at {CLAUDE_BUNDLE}")


def build_bundle() -> None:
    """Build both Cursor and Claude Code bundles."""
    build_cursor_bundle()
    build_claude_bundle()


if __name__ == "__main__":
    build_bundle()
