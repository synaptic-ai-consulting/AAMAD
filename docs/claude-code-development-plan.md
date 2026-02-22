# AAMAD Claude Code Support — Development Plan

This plan implements the changes required to support **Claude Code** as a first-class IDE target for AAMAD, as described in `aamad-ide-guide.md`. VS Code / GitHub Copilot support is out of scope for this phase and will be addressed later.

---

## 1. Goals & Success Criteria

| Goal | Success criterion |
|------|--------------------|
| Users can install AAMAD for Claude Code in one step | `aamad init --ide claude-code` (or `--ide claude_code`) produces a working `.claude/` tree |
| Claude Code loads all AAMAD rules | All 5 rule bodies are available (single CLAUDE.md or `.claude/rules/*.md`) |
| All personas are available in Claude Code | 7 agent files under `.claude/agents/` with correct Claude Code frontmatter |
| Phase 1 prompt is invocable | User can run a Phase 1–style flow via a Claude Code command/skill |
| No regression for Cursor users | Default `aamad init` (Cursor) behavior unchanged |

---

## 2. Current State Summary

| Asset | Location | Count / notes |
|-------|----------|----------------|
| Rules | `.cursor/rules/*.mdc` | 5 files: `aamad-core`, `development-workflow`, `adapter-crewai`, `adapter-registry`, `epics-index` |
| Agents | `.cursor/agents/*.md` | 7 personas: `product-mgr`, `system-arch`, `project-mgr`, `frontend-eng`, `backend-eng`, `integration-end`, `qa-eng` (+ `personas.md` index) |
| Prompts | `.cursor/prompts/` | 1 file: `prompt-phase-1` (no extension) |
| Templates | `.cursor/templates/` | IDE-agnostic; no conversion needed |
| Project context | `project-context/` | IDE-agnostic; no conversion needed |

---

## 3. Implementation Phases

### Phase 3.1 — Conversion logic (no CLI change yet)

Implement converters that turn Cursor artifacts into Claude Code artifacts. These will be used by the CLI and can be tested in isolation.

**3.1.1 Rule converter: `.mdc` → Claude Code**

- **Input:** `.cursor/rules/*.mdc` (YAML frontmatter + markdown body).
- **Output (choose one and implement):**
  - **Option A — Single file:** One `CLAUDE.md` at project root or `.claude/CLAUDE.md` with sections for each rule (e.g. `## AAMAD Core`, `## Development Workflow`, …). Strip frontmatter; keep only body; order by dependency (e.g. aamad-core first, then workflow, epics-index, adapter-registry, adapter-crewai).
  - **Option B — Split rules (recommended in guide):** `.claude/CLAUDE.md` (short summary + “see .claude/rules/”) plus `.claude/rules/<name>.md` per rule (e.g. `aamad-core.md`, `development-workflow.md`). Each file = one rule body, no frontmatter (Claude Code doesn’t use it for rules).
- **Implementation:** New module e.g. `src/aamad/claude_code.py` with:
  - `convert_rules(cursor_rules_dir: Path, out_dir: Path, style: "single" | "split")` that reads each `.mdc`, parses frontmatter (optional, for ordering), writes CLAUDE.md and/or `.claude/rules/*.md`.
- **Tests:** Unit tests: given 1–2 sample `.mdc` files, assert output structure and that rule body text is preserved.

**3.1.2 Agent converter: `.cursor/agents/*.md` → `.claude/agents/*.md`**

- **Input:** `.cursor/agents/*.md` (excluding `personas.md` if it’s only an index).
- **Output:** For each persona file, one `.claude/agents/<id>.md` with:
  - **Claude Code frontmatter** (see guide §4.1 Step 2): `name`, `description`, `tools`, `disallowedTools`, `model`, optionally `permissionMode`, `maxTurns`.
  - **Body:** Keep the markdown body (role, constraints, supported commands, inputs/outputs, prohibited actions); adjust heading/format only if needed for clarity.
- **Field mapping (Cursor → Claude Code):**
  - `agent.name` / `agent.id` → `name` (use `id` for file name and `name` for display in frontmatter or vice versa per Claude Code docs).
  - `agent.role` + `instructions` → `description` (concise sentence for when to use this agent).
  - `tools`: set a sensible default allowlist (e.g. Read, Edit, Write, Bash, Grep, Glob) and optionally restrict per persona (e.g. no WebFetch for backend).
  - `disallowedTools`: optional, from persona constraints.
  - `model`: `inherit`.
- **Implementation:** In `src/aamad/claude_code.py` (or `src/aamad/converters/agents.py`):
  - Parse Cursor YAML frontmatter + body.
  - Generate Claude Code frontmatter + same body (or lightly templated).
  - Write `.claude/agents/<id>.md`.
- **Edge case:** Ensure `integration-end` vs `integration-eng` naming is consistent (guide uses `integration-eng`; repo has `integration-end` — decide canonical id and stick to it).
- **Tests:** Unit tests: given one Cursor agent file, assert output frontmatter fields and that body content is present.

**3.1.3 Prompts → Claude Code command**

- **Input:** `.cursor/prompts/prompt-phase-1`.
- **Output:** `.claude/commands/phase-1-define.md` (or the exact name Claude Code expects for slash-commands). Content = prompt body so that `/phase-1-define` (or similar) runs Phase 1.
- **Implementation:** Simple copy or light wrapper in `claude_code.py` (e.g. `convert_prompts(cursor_prompts_dir, out_claude_commands_dir)`).
- **Tests:** Smoke test: file exists and contains expected prompt text.

**3.1.4 Settings**

- **Output:** `.claude/settings.json` with:
  - `permissions.allow` list (Bash for python/pip/crewai/npm/npx; Read/Edit with appropriate globs).
  - `env.AAMAD_ADAPTER`: `"crewai"`.
- **Implementation:** Either static JSON file in package data, or generated by a small function in `claude_code.py` that writes this file under `.claude/`.
- **Tests:** Assert file exists and is valid JSON with expected keys.

**Deliverable:** All conversion logic in code; unit tests passing; no CLI changes yet. Can be driven by a small script or `aamad convert --to claude-code` (see Phase 3.3).

---

### Phase 3.2 — CLI: `aamad init --ide claude-code`

Extend the installer so that when the user requests Claude Code, they get a `.claude/` tree instead of (or in addition to) `.cursor/`.

**3.2.1 Design choice: how to get `.claude/` content**

- **Option A — Transform on the fly:** `aamad init` always extracts the existing bundle (Cursor layout). If `--ide claude-code`, run the conversion functions on the extracted `.cursor/` (and prompts) to produce `.claude/` under `--dest`. No new bundle.
- **Option B — Separate bundle:** Ship a second artifact (e.g. `aamad_claude_bundle.zip`) that already contains a pre-built `.claude/`; `aamad init --ide claude-code` extracts that bundle. Requires building that bundle in `scripts/update_bundle.py` (or similar) from the converted output.
- **Recommendation:** **Option A** for v1: single bundle, transform after extract. Simpler and keeps one source of truth (Cursor artifacts). Option B can be a later optimization (e.g. faster init for Claude-only users).

**3.2.2 CLI changes**

- Add `--ide` (or `--target-ide`) to `aamad init` with choices: `cursor` (default), `claude-code` (and later `vscode`, `all`).
- Behavior:
  - `cursor`: current behavior (extract bundle to `--dest`; no conversion).
  - `claude-code`: extract bundle to a temp dir or in-place, then run rule + agent + prompt conversion and write `.claude/` under `--dest`; optionally write `.claude/settings.json`. Do not remove `.cursor/` if you extracted there (so `--ide all` later can share one extract). For `claude-code`-only, you can extract to temp and only write `.claude/` + `project-context/` + CHECKLIST/README to `--dest` to avoid putting `.cursor/` in a Claude-only project.
- **Documentation:** Update README “Install via pip / uv” section: add one line for Claude Code: “For Claude Code run `aamad init --ide claude-code` after install.”

**3.2.3 Dependencies**

- Conversion logic (Phase 3.1) must be callable from the CLI (e.g. `from aamad.claude_code import install_claude_code(dest, overwrite)`).

**Deliverable:** `uv run aamad init --ide claude-code --dest .` creates a valid `.claude/` (rules, agents, command, settings) and leaves `project-context/`, CHECKLIST, README usable. Manual smoke test in Claude Code: open project, confirm rules and agents appear, run Phase 1 command.

---

### Phase 3.3 — Optional: `aamad convert` subcommand

- **Purpose:** Allow users who already have a Cursor-initialized project to generate Claude Code artifacts without re-running `init` (e.g. `aamad convert --from cursor --to claude-code --dest .`).
- **Implementation:** Subparser `convert` with `--from`, `--to`, `--dest`. Reads from `--dest` (e.g. `.cursor/`, `.cursor/prompts/`) and writes `.claude/` under `--dest`. Reuses the same conversion functions as init.
- **Priority:** Can be Phase 3.4 or later; not required for “init for Claude Code” to be complete.

---

### Phase 3.4 — AGENTS.md bridge (recommended in guide)

- **Purpose:** Both Claude Code and VS Code can use a root-level `AGENTS.md` as a “README for agents.” Adding it improves discoverability and prepares for VS Code later.
- **Implementation:** Add a template or generator that writes a single `AGENTS.md` in `--dest` with:
  - Short intro that this project uses AAMAD.
  - List of agent personas (names + one-line role).
  - Workflow summary (Define → Build → Deliver).
  - Pointer to project-context and IDE-specific dirs (e.g. “See .claude/agents/ for Claude Code”).
- **When to write:** During `aamad init` (for any `--ide`) or at least when `--ide claude-code` or `--ide all`. Can be a separate small function called from init.
- **Deliverable:** `AGENTS.md` present after `aamad init --ide claude-code`.

---

## 4. Suggested Implementation Order

1. **Phase 3.1.1** — Rule converter (split style: `.claude/CLAUDE.md` + `.claude/rules/*.md`).
2. **Phase 3.1.2** — Agent converter (all 7 personas; fix integration-end vs integration-eng).
3. **Phase 3.1.3** — Prompt → command (phase-1-define).
4. **Phase 3.1.4** — `.claude/settings.json` generation.
5. **Phase 3.2** — Add `--ide` to `aamad init`, wire conversion into installer, test end-to-end.
6. **Phase 3.4** — Add `AGENTS.md` generation to init.
7. **Phase 3.3** — Optional `aamad convert` when needed.

---

## 5. File / Module Layout (proposal)

```
src/aamad/
  __init__.py
  cli.py              # add --ide, optional convert subcommand
  installer.py        # existing; optionally call claude_code.install_claude_code
  claude_code.py      # new: convert_rules, convert_agents, convert_prompts, write_settings, install_claude_code
  data/
    aamad_bundle.zip  # unchanged (Cursor + project-context + docs)
```

No new package data files required if using Option A (transform on the fly). If you add static `AGENTS.md` or `.claude/settings.json` templates, they can live under `src/aamad/data/` or in the bundle.

---

## 6. Testing Strategy

- **Unit:** Rule/agent conversion with 1–2 sample files; assert structure and content.
- **Integration:** Run `aamad init --ide claude-code --dest <tmpdir>`, assert `.claude/rules/`, `.claude/agents/`, `.claude/commands/`, `.claude/settings.json` exist and have expected content.
- **Manual:** In Claude Code, open the initialized project; confirm rules load, agents appear, and Phase 1 command runs without errors.

---

## 7. Out of Scope (for this plan)

- VS Code / GitHub Copilot support (separate plan after Claude Code works).
- `--ide all` (generate both .cursor and .claude) — can be added once `claude-code` is stable.
- Canonical cross-IDE agent schema (`.aamad/agents/*.yaml`) — deferred; current approach is Cursor as source, Claude Code as target.
- Changes to `project-context/` or `.cursor/templates/` (IDE-agnostic; no change).

---

## 8. Summary

| Phase | Deliverable |
|-------|-------------|
| 3.1   | Conversion logic (rules, agents, prompts, settings) + tests |
| 3.2   | `aamad init --ide claude-code` producing working `.claude/` |
| 3.3   | (Optional) `aamad convert --to claude-code` |
| 3.4   | `AGENTS.md` generated on init |

Completion of Phases 3.1, 3.2, and 3.4 gives users a single-command path to use AAMAD in Claude Code; 3.3 and `--ide all` can follow.
