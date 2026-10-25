# AAMAD Execution Checklist

This checklist guides you step-by-step through running AAMAD: greenfield starts at Phase 1 (Define); brownfield starts at Phase 0 (Review), then a constrained Define, then Phase 2 (Build) and Phase 3 (Deliver).  
**Artifacts** (`project-context/`, templates, Phase 0 / Phase 1 prompts) are the same in every IDE; **where agents and rules live** depends on how you initialized AAMAD.

---

## Install and IDE layout

- [ ] Install prerequisites (Python 3.9+, Node when your stack needs it; see [README.md](README.md)).
- [ ] Install AAMAD: `pip install aamad` or `uv pip install aamad`.
- [ ] Optional: run `aamad tutorial` for a terminal walkthrough of the crew workflow (`--list`, `--lesson`, `--print`).
- [ ] Initialize framework files for your IDE (pick one):

  | IDE | Command |
  | :-- | :------ |
  | **Guided setup** | `aamad init --dest .` (choose IDE, then greenfield or brownfield; greenfield also asks for a runtime adapter or “choose this later”) |
  | **Cursor** | `aamad init --ide cursor --dest .` |
  | **Claude Code** | `aamad init --ide claude-code --dest .` |
  | **VS Code + GitHub Copilot** | `aamad init --ide vscode --dest .` |
  | **Kiro** | `aamad init --ide kiro --dest .` |
  | **Non-interactive** | add `--mode greenfield` or `--mode brownfield`; on greenfield add `--runtime {crewai,claude-agent-sdk,cursor-sdk,later}` |

- [ ] Confirm expected outputs for **your** IDE (templates live in that IDE folder):

  - [ ] **Cursor:** `.cursor/agents/` (includes `ux-designer`), `.cursor/rules/` (includes `conciseness.mdc`), `.cursor/prompts/`, `.cursor/skills/` (`run-evals`, `draw-diagram`, `sync-docs`, `product-design`, `visual-regression`), `.cursor/templates/` (includes `ux-template.md`), root `AGENTS.md`
  - [ ] **Claude Code:** `.claude/` (`agents/` including `ux-designer`, `rules/`, `commands/`, `skills/` including `product-design` and `visual-regression`, `templates/`, `settings.json`), `AGENTS.md`
  - [ ] **VS Code + Copilot:** `.github/instructions/`, `.github/agents/` (includes `ux-designer`), `.github/prompts/` (includes `run-evals`, `draw-diagram`, `sync-docs`, `product-design`, `visual-regression`), `.github/skills/`, `.github/templates/`, `.vscode/settings.json`, `AGENTS.md`
  - [ ] **Kiro:** `.kiro/agents/` (includes `ux-designer`), `.kiro/steering/` (rules + manual Phase 0 / Phase 1 / sync-docs), `.kiro/skills/` (includes `product-design` and `visual-regression`), `.kiro/templates/` (includes `ux-template.md`), `AGENTS.md`

- [ ] Upgrading an existing project to 0.9.7: `aamad init --overwrite --ide <cursor|claude-code|vscode|kiro>` to pick up `@ux.designer`, `product-design`, `visual-regression`, and the UX templates. Claude Code, VS Code, or Kiro projects from 0.9.0 or earlier: if this project is not using Cursor, delete leftover `.cursor/`.

- [ ] Confirm `aamad.config.yml` exists with `project.mode` set by init. Optionally edit other preferences (or copy remaining keys from `aamad.config.example.yml`).
- [ ] Brownfield: `project-context/0.review/` exists; an existing project README was left in place.
- [ ] Skim root `AGENTS.md` so you know where personas live for your IDE.
- [ ] To **invoke personas** (`@product-mgr`, `@backend.eng`, …) and reference files, follow [README.md → Multi-IDE support](README.md#multi-ide-support) (Cursor, Claude Code, VS Code, and Kiro differ).

---

## Runtime target (Phase 2 generated MVP)

- [ ] Set `AAMAD_TARGET_RUNTIME` before Build-phase implementation work (greenfield `aamad init` may have already written it; “choose this later” leaves CrewAI as the default until you set it). Record the resolved value in `sad.md` Audit and other artifacts as rules require:

  - [ ] `crewai` (default if unset / unknown per adapter registry)
  - [ ] `claude-agent-sdk`
  - [ ] `cursor-sdk`

---

## Phase 0: Brownfield Review (`@system.arch`) — brownfield only

Skip this section when `project.mode` is `greenfield`.

- [ ] Invoke `@system.arch` (or open `.cursor/prompts/prompt-phase-0-review`; Claude Code: `/phase-0-review`; VS Code: phase-0-review prompt).
- [ ] Run `*review-codebase`
  - [ ] `project-context/0.review/current-state.md` — what the code does today
  - [ ] `project-context/0.review/documentation.md` — missing documentation (do not overwrite the repo README)
  - [ ] `project-context/0.review/architecture-backlog.md` — architectural actions only (not bug fixes)
- [ ] Run `*create-sad` (or `*create-sad --mvp` for a lean increment) using `sad-brownfield-template.md`
  - [ ] SAD describes the **current** solution
  - [ ] As-is pattern labeled observation, inference, or unknown
  - [ ] Proposed Enhancements chapter is present
  - [ ] Operator Decision is present (starts as `pending`)
  - [ ] Resolved `AAMAD_TARGET_RUNTIME` recorded in sad.md Audit
- [ ] Optionally run `aamad validate --phase review`.
- [ ] Operator records Operator Decision: `approved` | `approved-with-changes` | `rejected`.
- [ ] If `rejected`, revise the backlog and SAD; do not start Phase 1.
- [ ] If `approved` or `approved-with-changes`, continue to **constrained** Phase 1.

---

## Phase 1: Requirements Definition (`@product-mgr`)

- [ ] Invoke `@product-mgr` using your IDE’s agent chat (see **Install and IDE layout** and [README → Multi-IDE support](README.md#multi-ide-support)).
- [ ] **Brownfield:** do not start until SAD Operator Decision is `approved` or `approved-with-changes`. Scope PRD and stories to the approved enhancement set only. Skip MRD unless the operator asks for it.
- [ ] **Recommended for specialized greenfield projects:** run `*elicit-requirements` (or author `system-description.md` yourself) before MRD/PRD.
- [ ] **MRD decision (greenfield):**
  - [ ] Commercial / market-facing product → produce MRD
  - [ ] Internal / personal / operational tool → skip MRD; note rationale in PRD Assumptions
- [ ] Run as needed:
    - [ ] `*elicit-requirements` — System description (must do / must not / must cost / must prove; each row tagged requirement or assumption)
    - [ ] `*create-mrd` — Market Research Document at project-context/1.define/mrd.md using mrd-template.md in your IDE templates folder
    - [ ] `*create-prd` — Product Requirements Document at project-context/1.define/prd.md using prd-template.md in your IDE templates folder
    - [ ] `*create-context` — MRD (unless skipped) and PRD with context summary for handoff
    - [ ] `*create-stories` — MVP user stories under project-context/1.define/user-stories/
- [ ] Validate completeness: market analysis (when MRD produced), user personas, feature requirements, acceptance criteria, success metrics, and business/operational goals.
- [ ] Record assumptions and open questions in artifacts for downstream resolution.
- [ ] Approve context boundaries and artifacts for the next phase (greenfield → `@system.arch`; brownfield → `@ux.designer` if an approved enhancement adds a new surface, otherwise Build).

---

## Before Phase 2 Starts

- [ ] Ensure `project-context/1.define` includes:
  - [ ] prd.md (PRD) — **required**
  - [ ] mrd.md (MRD) — **optional** (required only for commercial/market-facing greenfield projects)
  - [ ] system-description.md — recommended when elicitation was used
  - [ ] sad.md (SAD — greenfield: after architecture step; brownfield: already written in Phase 0)
  - [ ] ux.md — **when UI is in scope** (greenfield after SAD; brownfield only for material UI enhancements). Approval `approved` or `approved-with-changes` before material frontend work.
- [ ] Brownfield: `project-context/0.review/` current-state, documentation, and architecture-backlog are present; Operator Decision is approved.
- [ ] Confirm framework layout from **Install and IDE layout** is still present (re-run `aamad init` with `--overwrite` only if you intend to refresh generated files).
- [ ] Confirm `AAMAD_TARGET_RUNTIME` is set to your chosen runtime (see **Runtime target** above).
- [ ] Optionally run `aamad validate --phase define`.

---

## Phase 2: Build Execution

Use the same persona invocation pattern as Phase 1 (Cursor `@name`, Claude Code by subagent name/description, VS Code dropdown or `@name` — see README).

### Step 0: Architecture Definition (`@system.arch`)

- [ ] **Greenfield:** Invoke `@system.arch`.
- [ ] **Greenfield:** Run `*decompose-work`, `*select-pattern`, and `*define-controls` before or as part of:
    - [ ] `*create-sad` — Generate full SAD at project-context/1.define/sad.md using sad-template.md in your IDE templates folder.
    - [ ] `*create-sad --mvp` — Lean SAD. May defer scale, not the pattern decision or the control register.
- [ ] Confirm SAD headings: Work Ownership, Pattern Decision, Reference Architecture, Model and Context Strategy, Control Register.
- [ ] **Brownfield:** SAD already exists from Phase 0; do not rewrite the as-is chapter unless the operator asked for a revision. Complete Work Ownership, Pattern Decision, Reference Architecture, Model and Context Strategy, and Control Register on the approved increment.
- [ ] Validate SAD completeness (greenfield: stakeholders/views/decisions; brownfield: as-is views + approved enhancements).
- [ ] Record assumptions and open questions in sad.md for downstream resolution.
- [ ] Record resolved `AAMAD_TARGET_RUNTIME` in the sad.md Audit section.
- [ ] Run `*define-eval-criteria` — fill the SAD evaluation criteria table (dimension, metric, threshold, grading method, source) before Build implementation starts. Requires a PRD.

---

### Step 0b: UX specification (`@ux.designer`) — when UI is in scope

- [ ] **Greenfield:** Invoke `@ux.designer` after SAD exists.
- [ ] **Brownfield:** Invoke `@ux.designer` only when an approved enhancement adds a new surface, flow, or interaction pattern. Skip for label/copy/reuse or backend-only work.
- [ ] Run `*design-ux`
  - [ ] Write `project-context/1.define/ux.md` from `ux-template.md`
  - [ ] Resolve `ui.design_system_mode` (`create` | `adopt` | `extend`) and `ui.design_system_source`
  - [ ] For a new surface, prototype the hardest screen under `project-context/1.define/prototypes/`
  - [ ] Leave Approval `pending` unless the operator already recorded a status
- [ ] Operator sets Approval: `approved` | `approved-with-changes` | `rejected`.
- [ ] Do not start material frontend work while Approval is `pending` or `rejected`.

---

### Step 1: Environment Setup (`@project.mgr`)

- [ ] Invoke `@project.mgr`.
- [ ] Run `*setup-project`
  - [ ] Scaffold directories and install required dependencies
  - [ ] Define environment variables (in .env or as described)
  - [ ] Document all actions in setup.md

---

### Step 2: Frontend Development (`@frontend.eng`)

- [ ] Invoke `@frontend.eng`.
- [ ] Run `*develop-fe`
  - [ ] Implement the approved `ux.md` contract (or record a skip if there is no user-facing UI)
  - [ ] Add UI stubs for future planned features
  - [ ] Apply approved tokens and the agreed responsive behavior
  - [ ] Render, exercise the primary task and failure paths, inspect agreed viewports
  - [ ] Write `project-context/2.build/ux-review.md`
  - [ ] After Human judgment, scaffold Playwright visual snapshots (`visual-regression` skill) or record **not tested** with rationale
  - [ ] Document all decisions and status in frontend.md

---

### Step 3: Backend Development (`@backend.eng`)

- [ ] Invoke `@backend.eng`.
- [ ] Run `*develop-be`
  - [ ] Scaffold backend runtime that implements the SAD Pattern Decision using the selected runtime adapter (`.cursor/rules/adapter-${AAMAD_TARGET_RUNTIME}.mdc` after init; paths differ by IDE but content is equivalent)
  - [ ] Do not introduce an agent loop, live-state retrieval, or a side-effecting tool the SAD did not allow
  - [ ] Add stub code for future/backlog logic
  - [ ] Implement the primary backend API endpoint
  - [ ] Document all work in backend.md

---

### Step 4: Integration (`@integration.eng`)

- [ ] Invoke `@integration.eng`.
- [ ] Run `*integrate-api`
  - [ ] Wire the PRD primary surface to the backend API
  - [ ] Test a basic round-trip on that flow
  - [ ] Document integration and known issues in integration.md

---

### Step 5: Quality Assurance (`@qa.eng`)

- [ ] Invoke `@qa.eng`.
- [ ] Run `*test-unit` — unit tests; map to AC-* IDs when available; log in qa.md
- [ ] Run `*test-integration` — integration tests across UI/API/runtime; log in qa.md
- [ ] Run `*qa` / `*verify-flow`
  - [ ] Perform smoke tests and functional tests on the primary UI flow
  - [ ] Verify frontend and backend are connected
  - [ ] When a UI exists, consume `ux.md` and `ux-review.md`; check accessibility, responsive behavior, and interface quality on changed routes
  - [ ] Run `*test-visual` when UI is in scope; a green visual run is not a Human judgment pass
  - [ ] Log issues, known gaps, and future work in qa.md
- [ ] Run `*verify-change` — correctness, security, maintainability, and a short explanation of what shipped (cite `ux-review.md` when UI changed)

---

### Step 5.4: Evaluation Strategy (`@qa.eng`) — required before Deliver when the Pattern Decision includes a model call

- [ ] Run `*run-evals` following `.cursor/skills/run-evals/SKILL.md`.
- [ ] Implement the SAD section 9 evaluation criteria table when present; otherwise answer the skill's operator gap check (thresholds, SLA, risk tolerance, dataset provenance, judge calibration).
- [ ] Build the golden dataset and graders; cover accuracy, latency, safety, security, and cost.
- [ ] Complete project-context/2.build/evals.md, including Production Monitoring Recommendations for `@devops.eng`.

---

### Step 5.5: Security Assessment (`@security.eng`) — required before Deliver under default config

- [ ] Invoke `@security.eng` (required when `aamad.config.yml` sets `security.require_security_assessment: true`; the 1.0 default).
- [ ] Run `*assess-security` (and `*scan-secrets` / `*review-deps` as needed).
- [ ] Verify each SAD Control Register row against the code.
- [ ] Complete project-context/2.build/security.md with severity-ranked findings.
- [ ] Route mitigations to owning personas; do not change app logic inside this persona.

---

### Step 6: Deliver (`@devops.eng`)

- [ ] Invoke `@devops.eng` after QA, evals, and security artifacts are complete (required under default config).
- [ ] Run `*prepare-release`
  - [ ] Confirm qa.md documents MVP verification (pass or scoped gaps) and the verification checklist
  - [ ] Confirm evals.md and fold its monitoring recommendations into deploy config
  - [ ] Confirm security.md (Control Register verified or accepted gaps)
  - [ ] Summarize release scope and version in deploy.md
- [ ] Run `*define-deploy` and `*configure-cicd`
  - [ ] Add minimal deploy and CI config aligned with SAD and AAMAD_TARGET_RUNTIME
  - [ ] When UI is in scope, include a generated visual-regression job (install browsers, run the recorded script)
  - [ ] Do not embed secrets; reference `.env.example` keys only
- [ ] Run `*document-deploy`
  - [ ] Complete project-context/3.deliver/deploy.md (hosting, access, rollback, live control register, Outcome Document, Audit)
- [ ] Run `*document-user-guide`
  - [ ] Complete project-context/3.deliver/user-guide.md
- [ ] Optionally run `aamad validate --phase deliver`.

---

### Step 7: Local MVP Launch

- [ ] Follow docs in setup.md and integration.md to run the full MVP locally
- [ ] Confirm the primary MVP use case works end-to-end
- [ ] Review all generated artifact files in project-context/2.build and 3.deliver

---

### Step 8: Prepare for Next Phase

- [ ] Archive all MVP milestone artifacts in project-context/2.build and 3.deliver
- [ ] List all deferred/backlog features in qa.md and/or as GitHub issues
- [ ] Share repo and context docs with team or community for feedback

---

## Maintenance: Documentation sync

After debugging or enhancing generated frontend, backend, or integration code, artifacts can drift from the implementation.

- [ ] Open a fresh chat and use `.cursor/prompts/prompt-sync-docs` (Claude Code: `/sync-docs`; VS Code: sync-docs prompt).
- [ ] Reconcile `project-context/2.build/*.md` (and deploy.md if needed) with the current codebase.
- [ ] Append Audit entries noting action `sync-docs` on each updated artifact.
- [ ] Re-run `aamad validate` for the relevant phase.

---

## Maintenance: Adopting evals in an existing project

For projects already at or past the QA stage without a SAD section 9 evaluation criteria table (built before this capability existed). This is the normal entry point for those projects, not a fallback — no back-to-Phase-1 rework required.

- [ ] Invoke `@qa.eng` and run `*run-evals` directly.
- [ ] Answer the skill's operator gap-check questions (thresholds, SLA, risk tolerance, dataset provenance, judge calibration) in place of the missing SAD table.
- [ ] Source golden-dataset items from the PRD and user stories, including inputs the current implementation was never exercised against — do not build the dataset only from cases already known to pass.
- [ ] Complete project-context/2.build/evals.md with agreed thresholds.
- [ ] Once evals.md exists, backfill sad.md section 9 from it via `.cursor/prompts/prompt-sync-docs` so future model/prompt changes have a real gate.
- [ ] Re-run `aamad validate --phase build`.

---

> For detailed guidelines and troubleshooting, see [README.md](README.md) and the templates and rules folders for your IDE.
