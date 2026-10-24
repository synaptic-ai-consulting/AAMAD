# AAMAD MVP System Architecture Document (SAD) Template

## Context & Instructions
Generate a system architecture specification for a multi-agent MVP.
Align agent and API design with the runtime selected via `AAMAD_TARGET_RUNTIME` (`crewai` | `claude-agent-sdk` | `cursor-sdk`) and the active adapter rule.
Derive the primary user-facing surface from the PRD (and `ux.md` when it exists). Do not default every application to a chat interface or dashboard. Do not hardcode a single vendor UI library as mandatory unless the PRD/SAD decisions require it.
This document is the blueprint for Build-phase personas. Prefer lean MVP views; defer nonessential NFRs to Future Work.

## Input Requirements

**PRD Document**: [REFERENCE `project-context/1.define/prd.md`]  
**MRD** (optional): [REFERENCE `project-context/1.define/mrd.md` OR N/A]  
**User Stories** (when present): [REFERENCE `project-context/1.define/user-stories/`]  
**MVP Scope**: Focus on core value proposition (80/20)  
**Selected Runtime**: [crewai | claude-agent-sdk | cursor-sdk]

## System Architecture Specification — Generate All Sections

### 1. MVP Architecture Philosophy & Principles

**MVP Design Principles**:

- Customer / operator feedback first  
- Minimal viable agent set and simplest orchestration that delivers core value  
- Observable by default (basic logging / health)  
- Automated deploy scaffolding from day 1 when Deliver phase is in scope

**Core vs Future Features**:

- **MVP**: Core functionality, the PRD-specified primary interface, essential integrations only  
- **Future**: Advanced features, enterprise security, horizontal scaling  
- Explicit exclusions and deferrals

**Technical Architecture Decisions**:

- Justify frontend framework choice (e.g. Next.js App Router when selected)  
- Justify UI approach for human-agent interaction  
- Define runtime-specific agent communication patterns  
- Specify streaming vs non-streaming requirements

### 2. Multi-Agent System Specification

**Agent Architecture Requirements**:

- Define 3–4 specialized agents maximum for MVP  
- Specify roles, goals, and collaboration patterns from PRD  
- Memory / session requirements (default: none or short-lived for reproducibility)  
- Tool / MCP integration needs per agent (least privilege)

**Task / Turn Orchestration**:

- Dependencies and execution flow  
- Expected outputs and data formats  
- Context passing between agents  
- Error handling, retries, cancellation / timeout behavior  
- Performance budgets (max execution time, token / turn limits)

**Runtime-Conditional Configuration** (fill the subsection matching Selected Runtime):

- **crewai**: crew composition, process type, YAML agent/task config, `max_iter`, task context chaining  
- **claude-agent-sdk**: coordinator + `AgentDefinition` specialists, hooks, `allowed_tools`, session policy  
- **cursor-sdk**: TypeScript/Node runtime roles, tool contracts, streaming/event envelopes, budget controls

### 3. Frontend Architecture Specification

**Technology Stack** (from PRD or justified defaults):

- Framework, UI library, styling, type safety, state management

**Application Structure**:

- Route / page organization  
- API client boundaries (no backend wiring in FE epic)  
- Component architecture and responsive / accessibility requirements

**Interface Requirements**:

- Primary interaction surface (from PRD/`ux.md`, not a presumed chat)  
- Loading / error states  
- Placeholders for Future Work features

### 4. Backend Architecture Specification

**API Architecture**:

- Chat (or primary) endpoint contract: request schema, response schema, streaming/event envelope  
- Validation, rate limiting, error envelope shape  
- Alignment with the selected runtime adapter

**Data Architecture** (MVP default: none unless PRD requires):

- Explicitly defer persistence when out of MVP; if included, justify minimal store

**Runtime Integration Layer**:

- How the HTTP/API layer invokes the selected runtime  
- Agent configuration management  
- Logging / Prompt Trace hooks per adapter Quality Gates

**Authentication & Secrets**:

- Env-var names only (from `.env.example`); no secret values in artifacts

### 5. DevOps & Deployment Architecture

**CI/CD** (minimal MVP): lint, test, build  
**Hosting**: smallest MVP-appropriate target; health-check endpoint  
**IaC / multi-region / advanced monitoring**: Future Work unless PRD requires  
**Observability**: baseline logs and health; advanced APM deferred unless scoped

### 6. Data Flow & Integration Architecture

- Request/response path from UI through API to runtime agents  
- External tool/API integrations required for MVP only  
- Error propagation and user-visible feedback

### 7. Performance & Scalability Specifications

- Response-time and concurrency targets for MVP  
- Scaling path deferred with rationale  
- Token / cost controls at runtime layer

### 8. Security & Compliance Architecture

- AuthN/AuthZ for MVP  
- Encryption and input validation baselines  
- Compliance deferred with explicit Open Questions when unknown

### 9. Testing & Quality Assurance Specifications

- Unit, integration, and smoke/acceptance expectations for MVP  
- Runtime-specific checks (task outputs, hook traces, schema validation)  
- Security assessment recommended before Deliver

**Evaluation Criteria** (when `*define-eval-criteria` has been run):

Measurable pass criteria across accuracy, latency, safety, security, and cost, derived from PRD KPIs, the SLA, and the consequence of a wrong output — not from what an early prototype happens to score. Ask the operator for thresholds that cannot be derived from inputs; do not invent them.

| ID | Dimension | Metric | Threshold | Grading Method | Source |
|----|-----------|--------|-----------|-----------------|--------|
| EC-001 | Accuracy | … | … | Code-based / LLM judge / Human | PRD §x / Operator answer |

`@qa.eng` implements this table via `*run-evals`, producing the golden dataset, graders, and `evals.md`. When this table is absent (projects predating this capability), `*run-evals` runs its own operator gap check instead of blocking.

### 10. MVP Launch & Feedback Strategy

- Beta / pilot criteria when applicable  
- Success metrics tied to PRD KPIs  
- Iteration priorities after first deploy

## Implementation Guidance for AI Development Agents

1. Foundation setup per `setup.md` epic  
2. Frontend MVP UI without backend wiring  
3. Backend runtime scaffolding per adapter rule  
4. Integration epic wires FE ↔ BE  
5. QA validates unit, integration, and smoke paths  
6. Deliver packages deploy/CI/runbook only

## Architecture Validation Checklist

- [ ] PRD requirements mapped to architectural components  
- [ ] Agents designed for the domain and selected runtime  
- [ ] Frontend and backend contracts agree on schemas / streaming  
- [ ] Secrets via env vars only  
- [ ] MVP vs Future Work boundaries explicit  
- [ ] Resolved `AAMAD_TARGET_RUNTIME` recorded in Audit

## Sources

- PRD, MRD (if any), user stories, adapter rule path

## Assumptions

- Stack defaults chosen when PRD was silent; list them explicitly

## Open Questions

- Unresolved NFR, hosting, or compliance items

## Audit

- Timestamp, persona id (`system-arch`), action (`create-sad` or `create-sad --mvp`), resolved `AAMAD_TARGET_RUNTIME`
