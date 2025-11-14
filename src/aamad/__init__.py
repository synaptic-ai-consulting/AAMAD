"""
AAMAD distribution package.

This package ships the framework artifacts (e.g., `.cursor/`, `project-context/`,
and supporting docs) together with a small utility API/CLI that can
materialize them into any target workspace.
"""

from __future__ import annotations

from importlib import metadata

from .installer import ArtifactInstaller, extract_artifacts, get_bundle_path

__all__ = [
    "ArtifactInstaller",
    "extract_artifacts",
    "get_bundle_path",
    "__version__",
]


def __getattr__(name: str) -> str:
    if name == "__version__":
        try:
            return metadata.version("aamad")
        except metadata.PackageNotFoundError:  # pragma: no cover - local dev
            return "0.0.0"
    raise AttributeError(name)

