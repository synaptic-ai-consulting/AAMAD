# AAMAD Execution Checklist

This checklist guides you step-by-step through running AAMAD from Phase 1 (Define) through Phase 2 (Build) and Phase 3 (Deliver), using the agentic workflows defined in the framework.  
**Artifacts** (`project-context/`, templates, Phase 1 prompt) are the same in every IDE; **where agents and rules live** depends on how you initialized AAMAD.

---

## Install and IDE layout

- [ ] Install prerequisites (Python 3.9+, Node when your stack needs it; see [README.md](README.md)).
- [ ] Install AAMAD: `pip install aamad` or `uv pip install aamad`.
- [ ] Initialize framework files for your IDE (pick one):

  | IDE | Command |
  | :-- | :------ |
  | **Guided setup** | `aamad init --dest .` (choose Cursor, Claude Code, VS Code with GitHub Copilot, or Kiro) |
  | **Cursor** | `aamad init --ide cursor --dest .` |
  | **Claude Code** | `aamad init --ide claude-code --dest .` |
  | **VS Code + GitHub Copilot** | `aamad init --ide vscode --dest .` |
  | **Kiro** | `aamad init --ide kiro --dest .` |

- [ ] Confirm expected outputs for **your** IDE (templates live in that IDE folder):

  - [ ] **Cursor:** `.cursor/agents/`, `.cursor/rules/`, `.cursor/prompts/`, `.cursor/skills/`, `.cursor/templates/`, root `AGENTS.md`
  - [ ] **Claude Code:** `.claude/` (`agents/`, `rules/`, `commands/`, `skills/`, `templates/`, `settings.json`), `AGENTS.md`
  - [ ] **VS Code + Copilot:** `.github/instructions/`, `.github/agents/`, `.github/prompts/` (includes `run-evals.prompt.md`), `.github/templates/`, `.vscode/settings.json`, `AGENTS.md`
  - [ ] **Kiro:** `.kiro/agents/`, `.kiro/steering/` (rules + manual Phase 1 / sync-docs), `.kiro/skills/`, `.kiro/templates/`, `AGENTS.md`

- [ ] Upgrading a Claude Code, VS Code, or Kiro project from 0.9.0 or earlier: `aamad init --overwrite --ide <claude-code|vscode|kiro>`. If this project is not using Cursor, delete leftover `.cursor/`.

- [ ] Optionally copy `aamad.config.example.yml` → `aamad.config.yml` and set project preferences.
- [ ] Skim root `AGENTS.md` so you know where personas live for your IDE.
- [ ] To **invoke personas** (`@product-mgr`, `@backend.eng`, …) and reference files, follow [README.md → Using AAMAD in your IDE](README.md#using-aamad-in-your-ide) (Cursor, Claude Code, VS Code, and Kiro differ).

---

## Runtime target (Phase 2 generated MVP)

- [ ] Set `AAMAD_TARGET_RUNTIME` before Build-phase implementation work (record the resolved value in `sad.md` Audit and other artifacts as rules require):

  - [ ] `crewai` (default if unset / unknown per adapter registry)
  - [ ] `claude-agent-sdk`
  - [ ] `cursor-sdk`

---

## Phase 1: Requirements Definition (`@product-mgr`)

- [ ] Invoke `@product-mgr` using your IDE’s agent chat (see **Install and IDE layout** and README → Using AAMAD in your IDE).
- [ ] **Recommended for specialized projects:** run `*elicit-requirements` (or author `system-description.md` yourself) before MRD/PRD.
- [ ] **MRD decision:**
  - [ ] Commercial / market-facing product → produce MRD
  - [ ] Internal / personal / operational tool → skip MRD; note rationale in PRD Assumptions
- [ ] Run as needed:
    - [ ] `*elicit-requirements` — System description at project-context/1.define/system-description.md
    - [ ] `*create-mrd` — Market Research Document at project-context/1.define/mrd.md using mrd-template.md in your IDE templates folder
    - [ ] `*create-prd` — Product Requirements Document at project-context/1.define/prd.md using prd-template.md in your IDE templates folder
    - [ ] `*create-context` — MRD (unless skipped) and PRD with context summary for handoff
    - [ ] `*create-stories` — MVP user stories under project-context/1.define/user-stories/
- [ ] Validate completeness: market analysis (when MRD produced), user personas, feature requirements, acceptance criteria, success metrics, and business/operational goals.
- [ ] Record assumptions and open questions in artifacts for downstream resolution.
- [ ] Approve context boundaries and artifacts for technical build phase.

---

## Before Phase 2 Starts

- [ ] Ensure `project-context/1.define` includes:
  - [ ] prd.md (PRD) — **required**
  - [ ] mrd.md (MRD) — **optional** (required only for commercial/market-facing projects)
  - [ ] system-description.md — recommended when elicitation was used
  - [ ] sad.md (SAD, after architecture step)
- [ ] Confirm framework layout from **Install and IDE layout** is still present (re-run `aamad init` with `--overwrite` only if you intend to refresh generated files).
- [ ] Confirm `AAMAD_TARGET_RUNTIME` is set to your chosen runtime (see **Runtime target** above).
- [ ] Optionally run `aamad validate --phase define`.

---

## Phase 2: Build Execution

Use the same persona invocation pattern as Phase 1 (Cursor `@name`, Claude Code by subagent name/description, VS Code dropdown or `@name` — see README).

### Step 0: Architecture Definition (`@system.arch`)

- [ ] Invoke `@system.arch`.
- [ ] Run one of:
    - [ ] `*create-sad` — Generate full SAD at project-context/1.define/sad.md using sad-template.md in your IDE templates folder.
    - [ ] `*create-sad --mvp` — Generate a lean MVP SAD, deferring nonessential components and NFRs; output to project-context/1.define/sad.md.
- [ ] Validate SAD completeness: stakeholders/concerns, views, quality attributes, decisions, constraints, and risks.
- [ ] Record assumptions and open questions in sad.md for downstream resolution.
- [ ] Record resolved `AAMAD_TARGET_RUNTIME` in the sad.md Audit section.
- [ ] Run `*define-eval-criteria` — fill the SAD section 9 evaluation criteria table (dimension, metric, threshold, grading method, source) before Build starts.

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
  - [ ] Implement MVP chat interface (or PRD-specified UI)
  - [ ] Add UI stubs for future planned features
  - [ ] Style and make the interface responsive
  - [ ] Document all decisions and status in frontend.md

---

### Step 3: Backend Development (`@backend.eng`)

- [ ] Invoke `@backend.eng`.
- [ ] Run `*develop-be`
  - [ ] Scaffold backend runtime and MVP runtime agent(s) using the selected runtime adapter (`.cursor/rules/adapter-${AAMAD_TARGET_RUNTIME}.mdc` after init; paths differ by IDE but content is equivalent)
  - [ ] Add stub code for future/backlog agent logic
  - [ ] Implement backend chat API endpoint
  - [ ] Document all work in backend.md

---

### Step 4: Integration (`@integration.eng`)

- [ ] Invoke `@integration.eng`.
- [ ] Run `*integrate-api`
  - [ ] Wire MVP frontend chat to backend chat API
  - [ ] Test basic chat round-trip functionality
  - [ ] Document integration and known issues in integration.md

---

### Step 5: Quality Assurance (`@qa.eng`)

- [ ] Invoke `@qa.eng`.
- [ ] Run `*test-unit` — unit tests; map to AC-* IDs when available; log in qa.md
- [ ] Run `*test-integration` — integration tests across UI/API/runtime; log in qa.md
- [ ] Run `*qa` / `*verify-flow`
  - [ ] Perform smoke tests and functional tests on chat flow
  - [ ] Verify frontend and backend are connected
  - [ ] Log issues, known gaps, and future work in qa.md

---

### Step 5.4: Evaluation Strategy (`@qa.eng`) — recommended before Security/Deliver

- [ ] Run `*run-evals` following `.cursor/skills/run-evals/SKILL.md`.
- [ ] Implement the SAD section 9 evaluation criteria table when present; otherwise answer the skill's operator gap check (thresholds, SLA, risk tolerance, dataset provenance, judge calibration).
- [ ] Build the golden dataset and graders; cover accuracy, latency, safety, security, and cost.
- [ ] Complete project-context/2.build/evals.md, including Production Monitoring Recommendations for `@devops.eng`.

---

### Step 5.5: Security Assessment (`@security.eng`) — recommended before Deliver

- [ ] Invoke `@security.eng` (required when `aamad.config.yml` sets `security.require_security_assessment: true`).
- [ ] Run `*assess-security` (and `*scan-secrets` / `*review-deps` as needed).
- [ ] Complete project-context/2.build/security.md with severity-ranked findings.
- [ ] Route mitigations to owning personas; do not change app logic inside this persona.

---

### Step 6: Deliver (`@devops.eng`)

- [ ] Invoke `@devops.eng` after QA artifacts are complete (and evals.md / security.md when available).
- [ ] Run `*prepare-release`
  - [ ] Confirm qa.md documents MVP verification (pass or scoped gaps)
  - [ ] Note evals.md status and fold its monitoring recommendations into deploy config
  - [ ] Note security.md status (present or accepted gap)
  - [ ] Summarize release scope and version in deploy.md
- [ ] Run `*define-deploy` and `*configure-cicd`
  - [ ] Add minimal deploy and CI config aligned with SAD and AAMAD_TARGET_RUNTIME
  - [ ] Do not embed secrets; reference `.env.example` keys only
- [ ] Run `*document-deploy`
  - [ ] Complete project-context/3.deliver/deploy.md (hosting, access control, rollback, Audit)
- [ ] Run `*document-user-guide`
  - [ ] Complete project-context/3.deliver/user-guide.md
- [ ] Optionally run `aamad validate --phase deliver`.

---

### Step 7: Local MVP Launch

- [ ] Follow docs in setup.md and integration.md to run the full MVP locally
- [ ] Confirm MVP chat use case works end-to-end
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
