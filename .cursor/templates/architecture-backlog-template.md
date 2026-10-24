# AAMAD Brownfield Architecture Backlog Template

## Context & Instructions
Recommend architectural actions to fix structural issues and evolve the existing solution.
This is **not** a bug list. Do not include drive-by refactors or feature requests that are not implied by the current structure.
Load `project-context/0.review/current-state.md` and `documentation.md` when present.
Every item must cite sources in the current tree (or current-state behavior IDs).

## Input Requirements

**Current-state dossier**: [REFERENCE `project-context/0.review/current-state.md`]  
**Review documentation**: [REFERENCE `project-context/0.review/documentation.md`]

## Architecture Backlog — Generate All Sections Below

### 1. Out of Scope

- Bug fixes
- Cosmetic cleanup
- New product features not implied by structural problems
- Hostile-target or binary analysis

### 2. Recommended Actions

Numbered items with stable IDs (`ARCH-001`, …).

| ID | Action | Problem it addresses | Evidence (path or BH-*) | Effort (S/M/L) | Priority (Must/Should/Could) |
|----|--------|----------------------|-------------------------|----------------|------------------------------|
| ARCH-001 | … | … | … | M | Should |

### 3. Suggested Sequence

- Ordered groups of ARCH-* IDs that should be adopted together
- Dependencies between items
- What can wait until after a first approved increment

### 4. Risks if Deferred

- Architectural risks that grow if the backlog is ignored
- Residual unknowns that block a recommendation (cite UNK-*)

## Sources

- current-state.md, documentation.md, and inspected source paths

## Assumptions

- Constraints assumed when recommending an evolution path

## Open Questions

- Decisions the operator must make before an item can be approved

## Audit

- Timestamp, persona id (`system-arch`), action (`review-codebase`)
