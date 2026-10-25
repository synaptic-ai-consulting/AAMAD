# AAMAD Security Assessment Template

## Context & Instructions
Verify the SAD Control Register against the implemented code, then record remaining findings.
Do not modify application business logic. Route mitigations to the owning persona.
Honor `aamad.config.yml` security preferences when present.

## Input Requirements

**SAD Control Register**: [REFERENCE `project-context/1.define/sad.md`]  
**QA**: [REFERENCE `project-context/2.build/qa.md`]  
**Implementation records**: backend.md, frontend.md, integration.md  
**Selected Runtime**: [crewai | claude-agent-sdk | cursor-sdk]

## Security Report — Generate All Sections Below

### 1. Control Register Verification

For each SAD Control Register row, record whether the control is present in code.

| ID | Control | Owner | Fail direction | Evidence path | Status (present / missing / drifted) | Notes |
|----|---------|-------|----------------|---------------|--------------------------------------|-------|
| CR-001 | … | … | fail closed | … | … | … |

Side-effecting controls must fail closed. Missing or drifted rows are findings below.

### 2. Findings

Severity-ranked: Critical / High / Medium / Low / Info.

| ID | Severity | Category | Location | Summary | Recommended owner |
|----|----------|----------|----------|---------|-------------------|
| SEC-001 | … | Control register / secrets / deps / other | path | … | @backend.eng |

Cover when in scope: direct injection, indirect injection, token-budget exhaustion, tool abuse, data exposure, fairness injection points, and reconstructable decision logs.

### 3. Secrets and Environment Handling

- Committed secrets or risky env handling
- `.env.example` names only; no secret values in this artifact

### 4. Dependency and Supply-Chain Notes

- MVP stack risks
- Deferred audits

### 5. Accepted Risks

| ID | Risk | Owner | Rationale |
|----|------|-------|-----------|
| … | … | … | … |

## Sources

- SAD Control Register, QA, implementation records, inspected paths

## Assumptions

- Accepted risks and operator attributions

## Open Questions

- Unresolved controls or compliance items

## Audit

- Timestamp, persona id (`security-eng`), action (`assess-security`), resolved `AAMAD_TARGET_RUNTIME`
