"""
Utility script to rebuild the embedded artifact bundle.

Usage:
    python scripts/update_bundle.py
"""

from __future__ import annotations

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "src" / "aamad" / "data" / "aamad_bundle.zip"
INCLUDE = [".cursor", "project-context", "CHECKLIST.md", "README.md"]


def build_bundle() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        OUT.unlink()

    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name in INCLUDE:
            path = ROOT / name
            if not path.exists():
                continue
            if path.is_file():
                zf.write(path, arcname=path.name)
                continue
            for file in path.rglob("*"):
                if file.is_dir():
                    continue
                rel = file.relative_to(ROOT)
                zf.write(file, arcname=str(rel))
    print(f"Updated bundle at {OUT}")


if __name__ == "__main__":
    build_bundle()

