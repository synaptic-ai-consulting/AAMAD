from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .installer import ArtifactInstaller, extract_artifacts, get_bundle_path
from .onboarding import (
    IDE_CHOICES,
    OnboardingCancelled,
    OnboardingNotInteractive,
    resolve_ide,
)
from .validator import format_report, validate_project

PHASE_CHOICES = ["auto", "define", "build", "deliver"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aamad",
        description=(
            "Install the AAMAD multi-agent framework artifacts into the current project."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    init_cmd = sub.add_parser("init", help="Copy artifacts into the destination folder.")
    init_cmd.add_argument(
        "--dest",
        type=Path,
        default=Path.cwd(),
        help="Output directory (defaults to current working directory).",
    )
    init_cmd.add_argument(
        "--ide",
        choices=IDE_CHOICES,
        default=None,
        help=(
            "Target IDE: cursor, claude-code, vscode, or kiro. "
            "Omit to choose interactively."
        ),
    )
    init_cmd.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting existing files.",
    )
    init_cmd.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview extracted files without writing.",
    )

    info_cmd = sub.add_parser(
        "bundle-info", help="Show the files bundled in the distribution."
    )
    info_cmd.add_argument(
        "--ide",
        choices=IDE_CHOICES,
        default="cursor",
        help="Which bundle to inspect: cursor (default), claude-code, vscode, or kiro (vscode and kiro use the cursor bundle).",
    )
    info_cmd.add_argument(
        "--verbose",
        action="store_true",
        help="Print one path per line instead of a summarized count.",
    )

    validate_cmd = sub.add_parser(
        "validate",
        help="Validate project-context artifacts against AAMAD quality gates.",
    )
    validate_cmd.add_argument(
        "--dest",
        type=Path,
        default=Path.cwd(),
        help="Project root containing project-context/ (default: cwd).",
    )
    validate_cmd.add_argument(
        "--phase",
        choices=PHASE_CHOICES,
        default="auto",
        help="Phase gate to enforce: auto (default), define, build, or deliver.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "init":
        try:
            ide = resolve_ide(args.ide)
        except OnboardingNotInteractive as exc:
            print(exc, file=sys.stderr)
            return 2
        except OnboardingCancelled as exc:
            print(exc, file=sys.stderr)
            return 2
        paths = extract_artifacts(
            destination=args.dest,
            ide=ide,
            overwrite=args.overwrite,
            dry_run=args.dry_run,
        )
        if args.dry_run:
            print("Would create:")
        else:
            print("Created:")
        for path in paths:
            print(f" - {path}")
        return 0

    if args.command == "bundle-info":
        installer = ArtifactInstaller(get_bundle_path(args.ide))
        files = installer.preview()
        if args.verbose:
            print("\n".join(files))
        else:
            print(f"{len(files)} files bundled ({args.ide})")
        return 0

    if args.command == "validate":
        result = validate_project(args.dest, phase=args.phase)
        print(format_report(result))
        return 0 if result.ok else 1

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
