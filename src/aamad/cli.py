from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .installer import ArtifactInstaller, extract_artifacts, get_bundle_path
from .onboarding import (
    DEFERRED_RUNTIME_MESSAGE,
    IDE_CHOICES,
    MODE_CHOICES,
    RUNTIME_CHOICES,
    OnboardingCancelled,
    OnboardingNotInteractive,
    resolve_ide,
    resolve_mode,
    resolve_runtime,
)
from .validator import format_report, validate_project

PHASE_CHOICES = ["auto", "review", "define", "build", "deliver"]

_NEXT_STEPS_INVOKE = {
    "brownfield": {
        "cursor": "In Cursor, open @system.arch (or .cursor/prompts/prompt-phase-0-review).",
        "claude-code": "In Claude Code, run /phase-0-review or ask the System Architect agent.",
        "vscode": "In VS Code, run the phase-0-review prompt with the System Architect agent.",
        "kiro": "In Kiro, open the System Architect agent (or /phase-0-review).",
    },
    "greenfield": {
        "cursor": "In Cursor, open @product-mgr (or .cursor/prompts/prompt-phase-1).",
        "claude-code": "In Claude Code, run /phase-1-define or ask the Product Manager agent.",
        "vscode": "In VS Code, run the phase-1-define prompt with the Product Manager agent.",
        "kiro": "In Kiro, open the Product Manager agent (or /phase-1-define).",
    },
}


def format_runtime_note(runtime: str) -> str:
    """Return the post-init message for a resolved runtime choice."""
    if runtime == "later":
        return DEFERRED_RUNTIME_MESSAGE
    return f"AAMAD_TARGET_RUNTIME set to {runtime}."


def format_next_steps(ide: str, mode: str) -> str:
    """Return suggested next actions after a successful init."""
    invoke = _NEXT_STEPS_INVOKE.get(mode, {}).get(
        ide,
        "Open the first persona for this project mode.",
    )
    if mode == "brownfield":
        return "\n".join(
            [
                "",
                "Next steps (brownfield):",
                f" 1. {invoke}",
                " 2. Run *review-codebase, then *create-sad.",
                " 3. Record the Operator Decision on project-context/1.define/sad.md.",
                " 4. When approved, invoke @product-mgr for a constrained PRD and stories.",
                " 5. If an approved enhancement adds a new surface, invoke @ux.designer for *design-ux.",
                " 6. Follow CHECKLIST.md Phase 0.",
            ]
        )
    return "\n".join(
        [
            "",
            "Next steps (greenfield):",
            f" 1. {invoke}",
            " 2. Run *elicit-requirements (recommended), then *create-prd and *create-stories.",
            " 3. Hand off to @system.arch for *create-sad.",
            " 4. When UI is in scope, invoke @ux.designer for *design-ux and approve ux.md.",
            " 5. Follow CHECKLIST.md Phase 1.",
        ]
    )


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
        "--mode",
        choices=MODE_CHOICES,
        default=None,
        help=(
            "Project mode: greenfield or brownfield. "
            "Omit to choose interactively; defaults to greenfield when not a TTY."
        ),
    )
    init_cmd.add_argument(
        "--runtime",
        choices=RUNTIME_CHOICES,
        default=None,
        help=(
            "Greenfield runtime adapter: crewai, claude-agent-sdk, cursor-sdk, "
            "or later. Omit to choose interactively on greenfield; skipped on "
            "brownfield. Non-TTY greenfield defaults to later (CrewAI until set)."
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
        help="Phase gate to enforce: auto (default), review, define, build, or deliver.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "init":
        try:
            ide = resolve_ide(args.ide)
            mode = resolve_mode(args.mode)
            runtime = resolve_runtime(args.runtime, mode)
        except OnboardingNotInteractive as exc:
            print(exc, file=sys.stderr)
            return 2
        except OnboardingCancelled as exc:
            print(exc, file=sys.stderr)
            return 2
        paths = extract_artifacts(
            destination=args.dest,
            ide=ide,
            mode=mode,
            runtime=runtime,
            overwrite=args.overwrite,
            dry_run=args.dry_run,
        )
        if args.dry_run:
            print("Would create:")
        else:
            print("Created:")
        for path in paths:
            print(f" - {path}")
        if mode == "greenfield" or runtime != "later":
            print()
            print(format_runtime_note(runtime))
        print(format_next_steps(ide, mode))
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
