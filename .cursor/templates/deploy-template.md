# AAMAD Deploy Runbook Template

## Context & Instructions
Document hosting, access, rollback, the live control register, and the outcome document.
Generate CI and deploy config only. Do not embed secrets.

## Input Requirements

**QA / evals / security**: [REFERENCE `project-context/2.build/qa.md`, `evals.md`, `security.md`]  
**SAD**: [REFERENCE `project-context/1.define/sad.md`]  
**Selected Runtime**: [crewai | claude-agent-sdk | cursor-sdk]

## Runbook — Generate All Sections Below

### 1. Release scope

- Version and summary
- QA status; evals.md status; security.md status

### 2. Hosting and CI

- Hosting target, ports, health-check endpoint
- Start command aligned with `AAMAD_TARGET_RUNTIME`
- CI stages: lint, test, build (plus visual job when UI is in scope)

### 3. Environment and access

- Env-var names from `.env.example` only
- Least-privilege access for runtime keys and deployment credentials

### 4. Live Control Register

Carry the SAD Control Register forward with live evidence paths.

| ID | Control | Owner | Fail direction | Live evidence | Escalation path |
|----|---------|-------|----------------|---------------|-----------------|
| CR-001 | … | … | fail closed | … | … |

### 5. Spend and rate posture

- Per-request ceiling and rate cap from `aamad.config.yml` `spend`
- Model allowlist from `model`

### 6. Observability

- Per-request traces (model/version, tokens, latency, stop reason, tool calls)
- Aggregate dashboards (cost, p50/p95, success rate, error types)
- Business-KPI translation from evals.md

### Outcome Document

- **Before metric**: …
- **Auditable control**: …
- **Measurement owner**: …
- **When the after metric will be recorded**: …
- **Reuse note**: …

### 7. Rollback

- Model or prompt change rollback criterion (written before the swap)
- Deployment rollback steps

## Sources

- SAD, evals.md, security.md, setup.md

## Assumptions

- Hosting target and accepted gaps

## Open Questions

- Unresolved promotion or measurement items

## Audit

- Timestamp, persona id (`devops-eng`), action (`document-deploy`), resolved `AAMAD_TARGET_RUNTIME`
