# AAMAD UX Specification Template

## Context & Instructions
Write the interaction and visual contract for this increment. Link the PRD and SAD; do not duplicate them. Keep implemented tokens in the codebase. Follow `.cursor/skills/product-design/SKILL.md`.
Greenfield: design the MVP surfaces named in the PRD/SAD. Brownfield: design only approved enhancements; the live UI is the system unless the operator adopted an external source.
Do not invent product requirements, backend capabilities, or a chat/dashboard default.

## Input Requirements

**PRD**: [REFERENCE `project-context/1.define/prd.md`]
**SAD**: [REFERENCE `project-context/1.define/sad.md`]
**User Stories** (when present): [REFERENCE `project-context/1.define/user-stories/`]
**Design-system mode**: [create | adopt | extend — from `aamad.config.yml` `ui.design_system_mode` or the default for project.mode]
**Design-system source** (adopt): [WORKSPACE PATH, or N/A]
**Review / as-is UI** (brownfield): [REFERENCE `project-context/0.review/current-state.md` AND live UI PATHS]

## UX Specification — Generate All Sections Below

### 1. User and task

- Who is acting
- What they need to accomplish
- The primary action
- Constraints that shape the experience (time, environment, permissions)

### 2. Flow and structure

- Entry points
- Navigation
- Screen hierarchy
- Exits
- Recovery paths

When this section needs a figure, draw it with `.cursor/skills/draw-diagram/SKILL.md` under `project-context/diagrams/ux-designer/`.

### 3. Visual direction

- Reference designs (workspace path or operator-confirmed URL)
- What to borrow from each (hierarchy, density, navigation, or visual language)
- What not to copy

### 4. System references

- Canonical source: `create` inventory, adopted workspace path, or live UI paths (`extend`)
- Semantic color roles and values this increment will use
- Typography scale
- Spacing scale
- Approved components and variants this increment may add
- Token mapping target in the stack (CSS variables, Tailwind theme, or equivalent)

Do not paste a second brand book. Extract only enforceable values. Do not rewrite the operator-supplied source.

### 5. State matrix

| State | Screen / route | What the user sees | Next useful action |
|-------|----------------|--------------------|--------------------|
| Loading | | | |
| Empty | | | |
| Populated | | | |
| Validation | | | |
| Error | | | |
| Permission | | | |

Add agent states (running, waiting-for-input, approval-required, failed, cancelled, partial) only when the SAD includes those states. Distinguish a proposed action from an executed action. See `.cursor/skills/product-design/states.md`.

### 6. Responsive behavior

- Viewport sizes to design and later inspect
- What stacks, hides, or moves at each size
- What stays persistent (primary action, status, errors)

### 7. Acceptance criteria

Observable conditions linked to user-story IDs (AC-* / US-*). Each row must be exercisable in a rendered interface.

| ID | Criterion | Story | How it is observed |
|----|-----------|-------|--------------------|
| UX-001 | | | |

### 8. Prototype (when the surface is new)

- Hardest screen and why
- Path: `project-context/1.define/prototypes/<slug>.html`
- Brownfield: enhancement screen only — not a replacement shell

## Assumptions and approval

**Approval status**: `pending`

Allowed values: `pending` | `approved` | `approved-with-changes` | `rejected`.
`@frontend.eng` implements material UI only when status is `approved` or `approved-with-changes`.

- Unresolved decisions
- Operator choices already recorded
- Skip rationale when this increment has no material UI

## Sources

- PRD / SAD / story paths
- Design-system source path or live UI paths
- Operator answers during intake

## Open Questions

- Unreadable external source, brand-vs-live-UI conflicts, or `libraries.forbidden` clashes

## Audit

- Persona id, action (`design-ux`), timestamp, resolved `ui.design_system_mode`, resolved `project.mode`
