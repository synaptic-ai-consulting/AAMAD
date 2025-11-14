from __future__ import annotations

import shutil
import zipfile
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Iterable, Iterator

BUNDLE_NAME = "data/aamad_bundle.zip"


def get_bundle_path() -> Path:
    """Return a filesystem path to the embedded artifact bundle."""
    with resources.as_file(resources.files("aamad") / BUNDLE_NAME) as bundle:
        return bundle


def extract_artifacts(
    destination: Path | str,
    *,
    overwrite: bool = False,
    dry_run: bool = False,
) -> list[Path]:
    """
    Extract the bundled artifacts into ``destination``.

    Args:
        destination: Directory that should receive `.cursor/`, `project-context/`, etc.
        overwrite: If False, raises FileExistsError when target already exists.
        dry_run: When True, no files are written; returns the would-be paths.
    """
    installer = ArtifactInstaller(get_bundle_path())
    return installer.extract(Path(destination), overwrite=overwrite, dry_run=dry_run)


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

