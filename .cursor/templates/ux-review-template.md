# AAMAD UX Review Template

## Context & Instructions
Record a rendered-interface review against the approved UX contract. Never claim visual verification from source inspection alone. Follow `.cursor/skills/product-design/SKILL.md`.
Greenfield: review the MVP surfaces in `ux.md`. Brownfield: review **changed routes and states** unless the approved enhancement is a redesign.
An LLM self-rating is not the sole acceptance decision.

## Input Requirements

**UX specification**: [REFERENCE `project-context/1.define/ux.md` OR N/A WITH SKIP RATIONALE]
**PRD / stories**: [REFERENCE]
**frontend.md**: [REFERENCE]
**Renderer**: [Cursor browser | control-ui | Playwright Test | other]
**Viewports inspected**: [LIST ACTUAL SIZES]

## Review — Generate All Sections Below

### 1. Scope

- Routes and states exercised
- Routes and states **not tested**
- Tool used and viewport sizes actually inspected
- Evidence directory or screenshot paths

### 2. Functional gate

Primary task completion, validation, navigation, recovery, permissions.

| ID | Route | State | Viewport | Result | Evidence | Notes |
|----|-------|-------|----------|--------|----------|-------|
| F-001 | | | | passed / failed / not tested | | |

### 3. Mechanical gate

Automated accessibility checks, overflow, broken controls, and Playwright Test visual snapshots. Contrast, target size, and keyboard: see `.cursor/skills/product-design/accessibility.md`. Visual snapshots: see `.cursor/skills/visual-regression/SKILL.md`.

| ID | Check | Tool | Result | Evidence | Notes |
|----|-------|------|--------|----------|-------|
| M-001 | Keyboard, primary task | manual | passed / failed / not tested | | |
| M-002 | Visible focus | manual | passed / failed / not tested | | |
| M-003 | Contrast spot check | | passed / failed / not tested | | |
| M-004 | Target size | | passed / failed / not tested | | |
| M-005 | Automated a11y scan | | passed / failed / not tested | | |
| M-006 | Visual regression | Playwright Test | passed / failed / not tested | spec + snapshot dir | |

A passing scan with no manual keyboard pass is **not tested** for keyboard operability. A green visual run is not a Human judgment pass.

### 3b. Visual regression

- Command (for example `npm run test:visual`)
- Browser channel and viewports
- Snapshot directory
- Last baseline Audit (persona, timestamp, operator approval for updates)
- Skip rationale when **not tested** (no UI, brownfield small change, or operator declined)

### 4. Human judgment gate

Hierarchy, clarity, density, visual coherence, suitability for the intended user, and divergence from `ux.md` System references.

| ID | Finding | Route | State | Viewport | User impact | Severity | Resolution | Evidence |
|----|---------|-------|-------|----------|-------------|----------|------------|----------|
| H-001 | | | | | | high / medium / low | open / fixed / accepted | |

### 5. Findings

Prioritized list. Each finding must include route, state, viewport, evidence, user impact, severity, and resolution. Do not collapse **not tested** into **passed**.

### 6. Remaining limitations

- Open findings that do not block this increment
- Checks recorded as **not tested**
- Brownfield surfaces left out of scope

## Sources

- `ux.md`, PRD, stories, `frontend.md`, evidence paths

## Assumptions

- Skip rationale when `ux.md` is absent on a brownfield small change
- Operator-accepted deviations from System references

## Open Questions

- Unresolved visual or interaction conflicts

## Audit

- Persona id, action (`review-ui`), timestamp, renderer, viewports, resolved `project.mode`
