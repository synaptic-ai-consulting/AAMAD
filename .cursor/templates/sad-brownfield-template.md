# AAMAD Brownfield System Architecture Document (SAD) Template

## Context & Instructions
Describe the **current** solution as it exists in the repository, then propose an enhancement roadmap.
This is not a greenfield multi-agent MVP SAD. Do not force runtime-agent or chat-UI sections onto a system that does not have them.
Load `.cursor/rules/brownfield-review.mdc` and the Review artifacts. Prefer observation over inference.
Do not modify application code. Architectural issues only — not bug fixes.

## Input Requirements

**Current-state dossier**: [REFERENCE `project-context/0.review/current-state.md`]  
**Review documentation**: [REFERENCE `project-context/0.review/documentation.md`]  
**Architecture backlog**: [REFERENCE `project-context/0.review/architecture-backlog.md`]  
**Selected Runtime** (if the existing or proposed system uses a generated runtime): [crewai | claude-agent-sdk | cursor-sdk | N/A]  
**MVP / increment scope**: Approved enhancement set only after Operator Decision

## System Architecture Specification — Generate All Sections

### 1. Current Solution Overview

- What the system is and who uses it
- Primary capabilities observed today (cite BH-* IDs)
- Boundaries: what is in-repo vs external

### 2. Logical View

- Major modules / bounded contexts and their responsibilities
- Key interfaces between them
- Element catalog (name, responsibility, notable files)

### 3. Process and Runtime View

- How the system starts and which processes run
- Request / job / event flows that were observed
- Timeouts, retries, and failure handling only when seen in code or config

### 4. Deployment View

- How it is packaged and hosted today (when observed)
- Environments, ports, and health checks (names only)
- Secrets via environment variable names only

### 5. Data View

- Stores, schemas, and migration approach when present
- Ownership of data and integration payloads
- Unobserved stores stay in Open Questions

### 6. Observed Quality Attributes

- Reliability, security, operability, and performance as evidenced
- Distinguish measured or configured values from inferred ones
- Gaps that are architectural (not defect reports)

### 7. Existing Architectural Decisions

| ID | Decision | Evidence | Status (in force / drifted / unknown) |
|----|----------|----------|----------------------------------------|
| AD-001 | … | … | in force |

Label the current application pattern as **observation**, **inference**, or **unknown**. Do not invent a greenfield multi-agent crew.

- **As-is primary shape** (if inferable): [augmented call | workflow | agent | unknown]
- **Evidence label**: observation | inference | unknown
- **Evidence**: path or BH-* / UNK-* ID

### 8. Architectural Risks and Technical Debt

- Structural risks only (coupling, missing boundaries, undocumented contracts)
- Do not list product bugs
- Link each risk to backlog IDs when a remediation exists

### 9. Proposed Enhancements

Derive this chapter from `architecture-backlog.md`. Group items into a recommended increment.

| ID | Enhancement | Rationale | Depends on | Suggested increment |
|----|-------------|-----------|------------|---------------------|
| ARCH-001 | … | … | — | 1 |

- Explicit exclusions and deferrals
- For `*create-sad --mvp`, include only the top-N items needed for a first increment

Fill the following decision headings for the **approved enhancement increment** only. `*create-sad --mvp` may defer scale, not these decisions. When a figure is needed, draw it with `.cursor/skills/draw-diagram/SKILL.md` under `project-context/diagrams/system-arch/`.

### Work Ownership

For each step in the approved increment: owner is model, existing system, or human. Collaborative draft-and-decide is allowed. Justify with reversibility, stakes, and who is accountable. Deterministic rules and live records stay in the system that already owns them.

| Step | Owner | Reversibility | Stakes | Accountable party | Rationale |
|------|-------|---------------|--------|-------------------|-----------|
| … | … | … | … | … | … |

**Feasibility verdict**: `feasible as scoped` | `feasible with constraints` | `not feasible`  
**Load-bearing constraint** (when constrained): …

### Pattern Decision

- **Primary shape**: [augmented call | workflow | agent]
- **Workflow sub-shape** (when applicable): …
- **Deciding factor** (predictability, error cost, observability, latency, cost): …
- **Rejected alternatives and reversal cost**: …
- **Tool allowlist / Turn budget / Stop conditions** (required when Primary shape is agent): …

There is no fourth option named multi-agent. Sequence written in code is a workflow. A model that chooses the next role is an agent. Orchestrator plus subagents stays inside the agent pattern and needs a coverage check, retry or gap flag, orchestrator checkpoint, shared trace id, and a human gate before irreversible actions.

### Reference Architecture

- **Selected reference architecture**: …
- **Known failure this design prevents**: …
- **Second pattern** (only when two parts fail differently): … | none

Retrieval is forbidden as the source of live state.

### Model and Context Strategy

- **Default model tier**: balanced default unless a measured need requires another
- **Context strategy**: progressive
- **Swap-as-release rule**: eval gate and rollback criterion before any model or prompt change
- **Entry point** and **named tradeoff**: …
- **Identity**: enforced in server-side code

### Control Register

| ID | Risk category | Control | Control point | Failure direction | Owner | Evidence artifact | Review routing |
|----|---------------|---------|---------------|-------------------|-------|-------------------|----------------|
| CR-001 | … | … | input / output / tool-call | fail closed | … | … | … |

### Production Shape

- Cost and latency at expected volume for the increment
- Retries, fallback, circuit breaker
- Architecture-specific failure mode and mitigation
- Per-request traces separate from dashboards

### 10. Operator Decision

The operator records the decision here after reviewing the as-is architecture and proposed enhancements.
`@product-mgr` must not start constrained Define until **Status** is `approved` or `approved-with-changes`.

- **Status**: pending
- **Notes**: (operator)
- **Approved items** (when approved-with-changes): ARCH-* IDs
- **Rejected items**: ARCH-* IDs

Allowed status values: `pending` | `approved` | `approved-with-changes` | `rejected`

## Sources

- `project-context/0.review/current-state.md`
- `project-context/0.review/documentation.md`
- `project-context/0.review/architecture-backlog.md`
- Inspected source, tests, and config paths

## Assumptions

- Inferences used to complete views; mark them explicitly

## Open Questions

- Unresolved structure, hosting, or compliance items (include UNK-* IDs)

## Audit

- Timestamp, persona id (`system-arch`), action (`create-sad` or `create-sad --mvp`), resolved `AAMAD_TARGET_RUNTIME`
