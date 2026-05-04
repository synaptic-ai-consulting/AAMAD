# AAMAD Execution Checklist

This checklist guides you step-by-step through running AAMAD from Phase 1 (Define) through Phase 2 (Build), using the agentic workflows defined in the framework.  
**Artifacts** (`project-context/`, templates, Phase 1 prompt) are the same in every IDE; **where agents and rules live** depends on how you initialized AAMAD.

---

## Install and IDE layout

- [ ] Install prerequisites (Python 3.9+, Node when your stack needs it; see [README.md](README.md)).
- [ ] Install AAMAD: `pip install aamad` or `uv pip install aamad`.
- [ ] Initialize framework files for your IDE (pick one):

  | IDE | Command |
  | :-- | :------ |
  | **Cursor** (default) | `aamad init --ide cursor --dest .` |
  | **Claude Code** | `aamad init --ide claude-code --dest .` |
  | **VS Code + GitHub Copilot** | `aamad init --ide vscode --dest .` |

- [ ] Confirm expected outputs for **your** IDE (templates stay under `.cursor/templates/` for all):

  - [ ] **Cursor:** `.cursor/agents/`, `.cursor/rules/`, `.cursor/prompts/`, `.cursor/templates/`, root `AGENTS.md`
  - [ ] **Claude Code:** `.claude/` (`agents/`, `rules/`, `commands/`, `settings.json`), `.cursor/templates/`, `AGENTS.md`
  - [ ] **VS Code + Copilot:** `.github/instructions/`, `.github/agents/`, `.github/prompts/`, `.vscode/settings.json`, `.cursor/templates/`, `AGENTS.md`

- [ ] Skim root `AGENTS.md` so you know where personas live for your IDE.
- [ ] To **invoke personas** (`@product-mgr`, `@backend.eng`, …) and reference files, follow [README.md → Using AAMAD in your IDE](README.md#using-aamad-in-your-ide) (Cursor vs Claude Code vs VS Code differ).

---

## Runtime target (Phase 2 generated MVP)

- [ ] Set `AAMAD_TARGET_RUNTIME` before Build-phase implementation work (record the resolved value in `sad.md` Audit and other artifacts as rules require):

  - [ ] `crewai` (default if unset / unknown per adapter registry)
  - [ ] `claude-agent-sdk`
  - [ ] `cursor-sdk`

---

## Phase 1: Requirements Definition (`@product-mgr`)

- [ ] Invoke `@product-mgr` using your IDE’s agent chat (see **Install and IDE layout** and README → Using AAMAD in your IDE).
- [ ] Run one of:
    - [ ] `*create-mrd` — Generate Market Research Document at project-context/1.define/mrd.md using .cursor/templates/mrd-template.md.
    - [ ] `*create-prd` — Generate Product Requirements Document at project-context/1.define/prd.md using .cursor/templates/prd-template.md.
    - [ ] `*create-context` — Generate both MRD and PRD with context summary for handoff.
- [ ] Validate completeness: market analysis, user personas, feature requirements, success metrics, and business goals.
- [ ] Record assumptions and open questions in artifacts for downstream resolution.
- [ ] Approve context boundaries and artifacts for technical build phase.

---

## Before Phase 2 Starts

- [ ] Ensure `project-context/1.define` includes:
  - [ ] market-research-document.md (MRD)
  - [ ] product-requirements-document.md (PRD)
- [ ] Confirm framework layout from **Install and IDE layout** is still present (re-run `aamad init` with `--overwrite` only if you intend to refresh generated files).
- [ ] Confirm `AAMAD_TARGET_RUNTIME` is set to your chosen runtime (see **Runtime target** above).

---

## Phase 2: Build Execution

Use the same persona invocation pattern as Phase 1 (Cursor `@name`, Claude Code by subagent name/description, VS Code dropdown or `@name` — see README).

### Step 0: Architecture Definition (`@system.arch`)

- [ ] Invoke `@system.arch`.
- [ ] Run one of:
    - [ ] `*create-sad` — Generate full SAD at project-context/1.define/sad.md using .cursor/templates/sad-template.md.
    - [ ] `*create-sad --mvp` — Generate a lean MVP SAD, deferring nonessential components and NFRs; output to project-context/1.define/sad.md.
- [ ] Validate SAD completeness: stakeholders/concerns, views, quality attributes, decisions, constraints, and risks.
- [ ] Record assumptions and open questions in sad.md for downstream resolution.
- [ ] Record resolved `AAMAD_TARGET_RUNTIME` in the sad.md Audit section.

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
  - [ ] Implement MVP chat interface (Next.js, assistant-ui)
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
- [ ] Run `*qa`
  - [ ] Perform smoke tests and functional tests on chat flow
  - [ ] Verify frontend and backend are connected
  - [ ] Log issues, known gaps, and future work in qa.md

---

### Step 6: Local MVP Launch

- [ ] Follow docs in setup.md and integration.md to run the full MVP locally
- [ ] Confirm MVP chat use case works end-to-end
- [ ] Review all generated artifact files in project-context/2.build

---

### Step 7: Prepare for Next Phase

- [ ] Archive all MVP milestone artifacts in project-context/2.build and 3.deliver
- [ ] List all deferred/backlog features in qa.md and/or as GitHub issues
- [ ] Share repo and context docs with team or community for feedback

---

> For detailed guidelines and troubleshooting, see [README.md](README.md) and documentation in `.cursor/templates` and `.cursor/rules`.
