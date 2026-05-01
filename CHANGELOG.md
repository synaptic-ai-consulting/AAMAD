# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-05-01

### Added

- New runtime adapter rule: `adapter-claude-agent-sdk.mdc`. Generated MVPs can now target Claude Agent SDK runtime semantics via `AAMAD_TARGET_RUNTIME=claude-agent-sdk`.
- New development crew index file: `.cursor/agents/dev-crew.md`.
- Conformance tests ensuring both runtime adapter rules (`adapter-crewai`, `adapter-claude-agent-sdk`) are converted for Claude Code and VS Code bundles.

### Changed (BREAKING)

- Renamed environment variable `AAMAD_ADAPTER` to `AAMAD_TARGET_RUNTIME` (no alias).
- Re-scoped adapters from "AAMAD execution framework" to "runtime target for generated Phase 2 implementation."
- Updated core and registry rules to keep AAMAD crew orchestration adapter-neutral while runtime adapters govern generated backend conventions.
- Slimmed `adapter-crewai.mdc` to runtime-specific guidance and promoted shared policy language into `aamad-core.mdc`.
- Updated personas (`@backend.eng`, `@system.arch`, `@integration.eng`, `@qa.eng`) to follow selected runtime adapter semantics.
- Renamed `.cursor/agents/personas.md` to `.cursor/agents/dev-crew.md`.

### Deferred

- Cursor SDK runtime adapter (`cursor-sdk`) rule and scaffolding support deferred to v0.5.0.

### Out of scope

- Headless/programmatic orchestration of AAMAD's own Define → Build → Deliver phases.

## [0.3.0] - 2025-02-22

### Added

- **VS Code / GitHub Copilot support** — `aamad init --ide vscode` generates `.github/instructions/`, `.github/agents/`, `.github/prompts/`, and `.vscode/settings.json` from the Cursor bundle (transform on the fly). Enables use of AAMAD with GitHub Copilot Chat and custom agents, including handoffs for Define → Build → Deliver.
- New module `aamad.vscode_copilot`: rule converter (`.mdc` → `.instructions.md`), agent converter (with optional handoffs), prompt converter, and VS Code settings writer with merge support.
- `get_vscode_planned_paths()` for dry-run path listing.
- README section "VS Code + GitHub Copilot" with install steps, folder structure, and required extensions.

### Changed

- CLI `--ide` now accepts `cursor`, `claude-code`, and `vscode`.
- `extract_artifacts(ide="vscode")` extracts the Cursor bundle then runs VS Code conversion; AGENTS.md points to `.github/agents/` when IDE is vscode.
- README multi-IDE table extended with VS Code column.

## [0.2.0] - (previous)

- Claude Code support (`aamad init --ide claude-code`).
- AGENTS.md bridge file for IDE discoverability.

## [0.1.0] - (initial)

- Cursor-only installer and bundle.
- Core AAMAD rules, agents, templates, and project-context layout.
