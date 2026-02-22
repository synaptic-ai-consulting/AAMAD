# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
