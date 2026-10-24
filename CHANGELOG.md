# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.9.1] - 2026-10-24

### Changed

- Templates now live in each IDE folder instead of a leftover `.cursor/templates/` tree: `.claude/templates/`, `.github/templates/`, `.kiro/templates/`. Cursor is unchanged (`.cursor/templates/` remains the source of truth). Converted personas, rules, prompts, and skills rewrite `.cursor/templates/` references to the IDE path.
- `aamad init --ide vscode` no longer extracts the full Cursor tree. Like Kiro, it stages the Cursor bundle and writes only `.github/`, `.vscode/`, shared docs, and `project-context/`.
- Claude Code and Kiro installs no longer ship a `.cursor/` directory.

### Upgrade

- Existing Claude Code, VS Code, or Kiro projects: `aamad init --overwrite --ide <claude-code|vscode|kiro>`. If the project is not using Cursor, delete leftover `.cursor/` afterward.

## [0.9.0] - 2026-10-24

### Added

- **Kiro support** — `aamad init --ide kiro` converts the Cursor bundle into `.kiro/steering/`, `.kiro/agents/`, and `.kiro/skills/` (transform on the fly; no separate zip). Rules become always-on steering; personas become custom agents with `read`/`write`/`shell` (plus `web` for `@product-mgr` and `@system.arch`); `run-evals` copies as a native Agent Skill; Phase 1 and sync-docs prompts become manual steering. Shared output matches Claude Code: `project-context/`, `.cursor/templates/` only, docs, and `AGENTS.md`.
- Guided `aamad init`: omitting `--ide` prompts "Which development environment will you use the AAMAD dev crew on?" with arrow-key choices (Cursor, Claude Code, VS Code with GitHub Copilot, Kiro). Non-interactive runs without `--ide` exit 2 instead of defaulting to Cursor. `--ide` still skips the prompt for CI and scripts.

### Changed

- `--ide` on `init` is optional (no longer defaults to `cursor`). Library `extract_artifacts` still defaults to `cursor`.
- CLI `--ide` choices now include `kiro`.

## [0.8.0] - 2026-09-04

### Added

- Evaluation skill `.cursor/skills/run-evals/` (owned by `@qa.eng`, `*run-evals`): defines and implements the eval strategy from `project-context/` — golden dataset, code-based checks, LLM-as-judge scoring with calibration, and production monitoring recommendations for `@devops.eng`. Writes `project-context/2.build/evals.md` using the new `evals-template.md`.
- Operator gap-check in the skill: when business context needed for thresholds/SLA/risk tolerance is missing, the agent asks the operator in a single batched round (via `AskQuestion` in Cursor, a numbered list elsewhere) instead of inventing values; answers are recorded in `evals.md` Assumptions.
- `@system.arch` action `*define-eval-criteria`: fills a new evaluation criteria table in SAD section 9 (dimension, metric, threshold, grading method, source) so eval design happens before Build, per standard eval-suite practice.
- New `Evals` epic in `epics-index.mdc`; `evals.md` wired as a recommended input to `@devops.eng` and the Deliver phase gate.
- Converters for the new skill: native `.claude/skills/run-evals/` for Claude Code; `.github/prompts/run-evals.prompt.md` bound to `qa-eng` for VS Code Copilot (no native skills primitive).
- CHECKLIST "Adopting evals in an existing project" maintenance section.

### Changed

- `aamad validate` treats `evals.md` as an optional Build artifact (warning-only, like `mrd.md`) and checks its terminal sections when present.

### Compatibility note

- The `@system.arch` eval-criteria step is **new-project guidance, not a prerequisite**. Projects that already reached QA (or further) before this release are not out of compliance: run `*run-evals` directly and answer its gap-check questions in place of the SAD table, then optionally backfill SAD section 9 from `evals.md` via `prompt-sync-docs`. `evals.md` stays at warning level in the validator and the SAD section 9 expansion is not a required heading, so upgrading mid-project does not fail any existing `aamad validate` gate.

## [0.7.5] - 2026-07-20

### Changed

- README aligned with v0.7.x workflow: phases diagram, Phase 2 unit/integration QA + security, Phase 3 Deliver section, How to Use (`aamad validate`, `aamad.config.yml`, sync-docs), and Core Concepts.

## [0.7.4] - 2026-07-20

### Added

- Structured requirements elicitation: `*elicit-requirements`, `system-description-template.md`, optional richer Phase 1 intake.
- Optional MRD path for internal/personal projects (checklist + persona + prompt).
- Explicit QA stages: `*test-unit` and `*test-integration` on `@qa.eng` with AC-* traceability.
- Documentation sync prompt: `.cursor/prompts/prompt-sync-docs` (Claude `/sync-docs`, VS Code `sync-docs.prompt.md`) and CHECKLIST Maintenance section.
- Security Engineer persona `@security.eng` → `project-context/2.build/security.md`, wired as recommended pre-Deliver gate.
- User guide generation: `user-guide-template.md` and `*document-user-guide` on `@devops.eng`.
- Project config: `aamad.config.example.yml` / template, core-rule Project Configuration section, `aamad validate` unknown-key checks.
- README "Principles and benefits" section.

### Changed

- Claude Code and VS Code converters include `security-eng` and sync-docs prompts; VS Code handoffs are QA → Security → DevOps.
- CHECKLIST, epics-index, delivery-workflow, and AGENTS.md updated for elicitation, security, and user docs.

## [0.7.3] - 2026-07-20

### Added

- `aamad validate` CLI: phase gates (define/build/deliver), required Sources/Assumptions/Open Questions/Audit headings, and `AAMAD_TARGET_RUNTIME` Audit checks.
- GitHub Actions CI workflow (`.github/workflows/ci.yml`) running pytest on Python 3.9–3.12.
- Bundle-freshness conformance tests so stale `src/aamad/data/*.zip` fails CI.
- `AGENTS.md` now stamps `Framework version:` from the installed package metadata.

### Changed

- `scripts/update_bundle.py` builders accept an optional output path for non-destructive rebuild checks.

## [0.7.2] - 2026-07-20

### Changed

- MRD, PRD, and SAD templates are runtime-neutral: parameterized by `AAMAD_TARGET_RUNTIME` instead of hardcoding CrewAI / Next.js + assistant-ui as the only stack.
- All Define templates (including SFS and user-story) end with required Sources, Assumptions, Open Questions, and Audit sections per `aamad-core`.

## [0.7.1] - 2026-07-20

### Fixed

- `adapter-registry.mdc` missing opening frontmatter delimiter so `alwaysApply` was not parsed.
- Canonical MRD naming: `mrd-template.md` / `mrd.md` (replaced `mr-template.md` / `mr.md` inconsistencies).
- Persona naming consistency: dotted invocation (`@backend.eng`) vs hyphenated ids (`backend-eng`) documented in `dev-crew.md`.

### Added

- Architecture epic row in `epics-index.mdc` (`@system.arch`, `*create-sad`).
- `sfs-template.md` and `user-story-template.md` for System Architect and Product Manager inputs.
- `*create-stories` on `@product-mgr`; Agent Contract frontmatter aligned with other personas.

### Changed

- Phase 1 prompt and README template references updated for `mrd` naming.
- `product-mgr.md` rewritten to the standard Agent Contract schema.

## [0.6.0] - 2026-07-20

### Added

- DevOps Engineer persona: `.cursor/agents/devops-eng.md` (`@devops.eng`) for Phase 3 (Deliver).
- Consolidated delivery rule: `.cursor/rules/delivery-workflow.mdc` (deploy, hosting, access control).
- Deploy epic in `epics-index.mdc`; primary artifact `project-context/3.deliver/deploy.md`.
- VS Code handoff from `@qa.eng` to `@devops.eng` (Define → Build → Deliver chain).

### Changed

- `dev-crew.md`, README, and CHECKLIST updated for Deliver phase workflow.
- Claude Code and VS Code converters include `devops-eng` and `delivery-workflow`.

## [0.5.0] - 2026-05-04

### Added

- New runtime adapter rule: `adapter-cursor-sdk.mdc`. Generated MVPs can now target Cursor SDK runtime semantics via `AAMAD_TARGET_RUNTIME=cursor-sdk`.
- Converter support and conformance tests now include all runtime adapter rules (`adapter-crewai`, `adapter-claude-agent-sdk`, `adapter-cursor-sdk`) for both Claude Code and VS Code outputs.

### Changed

- Promoted `cursor-sdk` from planned to supported in runtime registry and user-facing documentation.
- Updated runtime-aware personas (`@system.arch`, `@backend.eng`, `@integration.eng`, `@qa.eng`) with explicit cursor-sdk-compatible architecture, backend, integration, and QA guidance.
- Added light runtime-traceability guidance to `@frontend.eng` and `@product-mgr`.

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
