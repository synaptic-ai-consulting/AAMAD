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
