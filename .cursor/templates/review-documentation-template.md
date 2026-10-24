# AAMAD Brownfield Review Documentation Template

## Context & Instructions
Fill documentation gaps so humans and AAMAD agents can understand this existing project.
Write the missing context here. Do **not** overwrite the repository README or other existing docs.
If a topic is already documented in the repo, cite that path instead of rewriting it.
Load `project-context/0.review/current-state.md` when present.

## Input Requirements

**Repository root**: [WORKING TREE]  
**Current-state dossier**: [REFERENCE `project-context/0.review/current-state.md`]  
**Existing docs found**: [list paths or N/A]

## Review Documentation — Generate All Sections Below

### 1. Purpose and Audience

- What this project is for
- Who operates or develops it

### 2. How to Run

- Prerequisites
- Install / build / start commands (only when observed or already documented)
- Required environment variable *names* (never secret values)

### 3. Main Flows

- Primary user or operator journeys that the code supports today
- Link each flow to current-state behavior IDs (`BH-*`) when possible

### 4. Ownership and Layout

- Important directories and what they contain
- Suggested owners (team or persona) when known; otherwise unknown

### 5. Documentation Gap List

| ID | Missing topic | Suggested home (do not write there in this action) | Priority |
|----|---------------|-----------------------------------------------------|----------|
| DOC-001 | … | README / docs/… | Must / Should / Could |

## Sources

- Existing docs and current-state.md sections actually used

## Assumptions

- Gaps filled by inference; mark them explicitly

## Open Questions

- Docs that could not be reconstructed from the tree

## Audit

- Timestamp, persona id (`system-arch`), action (`review-codebase`)
