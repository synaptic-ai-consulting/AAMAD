# AAMAD Brownfield Current-State Template

## Context & Instructions
Describe what the existing codebase does today. This is a quickstart dossier for the human team and the AAMAD crew — not a full reverse-engineering report.
Load `.cursor/rules/brownfield-review.mdc`. Prefer source, tests, config, and existing docs over inference.
Distinguish observation vs inference vs unknown. Static reachability is not proof of runtime execution. Unobserved does not mean absent.
Do not invent product requirements. Do not propose bug fixes here.

## Input Requirements

**Repository root**: [WORKING TREE]  
**Selected Runtime** (optional at this stage): [crewai | claude-agent-sdk | cursor-sdk | undecided]  
**Existing docs** (if any): [README, docs/, comments]

## Current State — Generate All Sections Below

### 1. Target Identity

- Repository / package name and version (from manifests, not guesswork)
- Primary languages and runtimes
- Entry points (CLI, web, jobs, libraries)
- How the project is built and started (when documented or observed)

### 2. Structure Inventory

- Top-level packages / modules and their roles
- APIs, routes, or public interfaces
- UI surfaces
- Data stores and migration paths
- Background jobs, workers, or scheduled tasks
- External integrations (observed only)

### 3. Behavior Inventory

Numbered behaviors with stable IDs (`BH-001`, …). Ground each row in source, tests, or config.

| ID | Behavior | Where observed | Authority (observation / inference / unknown) |
|----|----------|----------------|-----------------------------------------------|
| BH-001 | … | path or test | observation |

### 4. Evidence Notes

- Claims that are directly supported by files or tests
- Inferences (and why they are inferences)
- What was not inspected

### 5. Unknowns Register

| ID | Question | Why it is unresolved | Suggested next inspection |
|----|----------|----------------------|---------------------------|
| UNK-001 | … | … | … |

## Sources

- File paths, manifests, tests, and existing docs actually read

## Assumptions

- Inferences used to fill gaps; mark them explicitly

## Open Questions

- Items the unknowns register could not close

## Audit

- Timestamp, persona id (`system-arch`), action (`review-codebase`)
