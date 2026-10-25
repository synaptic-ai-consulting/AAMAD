# AAMAD MVP System Architecture Document (SAD) Template

## Context & Instructions
Generate a system architecture specification for the MVP.
Record work ownership and a pattern decision before designing runtime roles. Do not default to a multi-agent crew or a chat interface.
Align API and runtime design with `AAMAD_TARGET_RUNTIME` (`crewai` | `claude-agent-sdk` | `cursor-sdk`) and the active adapter rule after the pattern is chosen.
Derive the primary user-facing surface from the PRD (and `ux.md` when it exists). Do not default every application to a chat interface or dashboard. Do not hardcode a single vendor UI library as mandatory unless the PRD/SAD decisions require it.
This document is the blueprint for Build-phase personas. Prefer lean MVP views; defer nonessential NFRs to Future Work. `*create-sad --mvp` may defer scale, not the pattern decision or the control register.
When a figure is needed, draw it with `.cursor/skills/draw-diagram/SKILL.md` under `project-context/diagrams/system-arch/`.

## Input Requirements

**PRD Document**: [REFERENCE `project-context/1.define/prd.md`]  
**MRD** (optional): [REFERENCE `project-context/1.define/mrd.md` OR N/A]  
**System Description** (when present): [REFERENCE `project-context/1.define/system-description.md`]  
**User Stories** (when present): [REFERENCE `project-context/1.define/user-stories/`]  
**MVP Scope**: Focus on core value proposition (80/20)  
**Selected Runtime**: [crewai | claude-agent-sdk | cursor-sdk]

## System Architecture Specification — Generate All Sections

### Work Ownership

For each user-visible step, assign one owner: model, existing system, or human. Collaborative draft-and-decide is allowed. Justify with reversibility, stakes, and who is accountable.

Deterministic rules and live records stay in the system that already owns them. Use the four behavior properties (probabilistic output, knowledge cutoff, limited working memory, steerability) as the lens.

| Step | Owner (model / existing system / human / collaborative) | Reversibility | Stakes | Accountable party | Rationale |
|------|----------------------------------------------------------|---------------|--------|-------------------|-----------|
| … | … | … | … | … | … |

**Feasibility verdict**: `feasible as scoped` | `feasible with constraints` | `not feasible`  
**Load-bearing constraint** (required when the verdict is constrained): …

### Pattern Decision

Choose exactly one primary shape: `augmented call` | `workflow` | `agent`. There is no fourth option named multi-agent.

If workflow, name the sub-shape: chaining, routing, parallelization, evaluator-optimizer, or a justified combination.

Walk predictability, error cost, observability, latency, and cost. The first factor that rules a pattern out is the decision. Record rejected alternatives and reversal cost.

- **Primary shape**: [augmented call | workflow | agent]
- **Workflow sub-shape** (when applicable): [chaining | routing | parallelization | evaluator-optimizer | combination: …]
- **Deciding factor**: …
- **Rejected alternatives and reversal cost**: …
- **Progression used**: prompt → tools or retrieval → evaluator-optimizer → fine-tuning last (confirm availability before recommending fine-tuning)

Agent is legal only when the path cannot be enumerated and error cost is acceptable and recoverable. Record:

- **Tool allowlist**: …
- **Turn budget**: …
- **Stop conditions**: …

Several named model roles are classified by who owns the sequence:

- Sequence written in code or runtime config, each role a bounded step → workflow (a sequential crew, a prompt chain, parallel specialist calls).
- A model chooses which role or tool runs next → agent.

When one model context cannot hold the work, use orchestrator plus scoped subagents **inside the agent pattern**. Record result schema, conflict rule, coverage check (results returned must equal units dispatched), retry or gap flag, orchestrator checkpoint, one shared trace id, and a human gate before irreversible subagent actions. Use the fewest subagents that meet the requirement. Do not add swarm, group chat, debate, peer handoff, blackboard, auctions, or nested manager trees.

The AAMAD development crew is outside this choice. `crew.autonomy` governs those personas.

### Reference Architecture

Pick the closest proven shape and name its known failure.

| Shape | Use when | Known failure to prevent |
|-------|----------|--------------------------|
| Agent | Path cannot be written in advance | Unbounded tools |
| Retrieval | Stable documents, not live state | Retrieval used as a substitute for live state |
| Document pipeline | Structured extraction with an exception path | No exception path |
| Routing | Inputs vary in kind | No human escalation, or an agent shipped before the routed workflow was measured |
| Coding agent | Agentic exploration, then deterministic edit/test/review | Edits without review or an eval |

- **Selected reference architecture**: …
- **Known failure this design prevents**: …
- **Second pattern** (only when two parts of the problem fail differently): … | none

Retrieval is forbidden as the source of live state. That case is a tool call.

### Model and Context Strategy

- **Default model tier**: balanced default unless a measured need requires another tier
- **Context strategy**: progressive — only what the step needs
- **Swap-as-release rule**: every model or prompt change is a release with an eval gate and a rollback criterion written before the swap
- **Entry point**: hosted chat | direct API | agent SDK | coding agent | MCP or tool server
- **Entry-point tradeoff named at decision time**: …
- **Entry-point responsibility map** (when more than one route exists): …
- **Minimum data in the context window**: …
- **Identity**: enforced in server-side code, not in the prompt

This entry point is the product’s route to the model. It is not the IDE chosen at `aamad init`, and it is not `AAMAD_TARGET_RUNTIME` unless this SAD explicitly says they are the same system.

### Control Register

Separate what training already reduces from what the application must enforce.

Three control points: input screening, output screening, tool-call authorization. Each control has a failure direction; side effects fail closed. Review routing uses confidence, reversibility, and error cost, not volume. The reviewer receives the inputs and the reason for the flag.

| ID | Risk category | Control | Control point (input / output / tool-call) | Failure direction (fail closed / fail open) | Owner | Evidence artifact | Review routing |
|----|---------------|---------|--------------------------------------------|---------------------------------------------|-------|-------------------|----------------|
| CR-001 | … | … | … | fail closed | … | … | … |

Cover when in scope: direct injection, indirect injection via retrieval or tools, token-budget exhaustion, tool abuse, data exposure, fairness injection points (corpus, prompt framing, examples, routing), and a decision log that can reconstruct why an output was produced.

### Production Shape

- Cost and latency at **expected volume**, not prototype volume
- Retries with backoff, fallback chain, and circuit breaker
- Failure mode specific to the chosen architecture, and its mitigation
- Per-request traces designed separately from aggregate dashboards

### 1. MVP Architecture Philosophy & Principles

**MVP Design Principles**:

- Customer / operator feedback first  
- Simplest orchestration that delivers core value (the recorded pattern)  
- Observable by default (basic logging / health)  
- Automated deploy scaffolding from day 1 when Deliver phase is in scope

**Core vs Future Features**:

- **MVP**: Core functionality, the PRD-specified primary interface, essential integrations only  
- **Future**: Advanced features, enterprise security, horizontal scaling  
- Explicit exclusions and deferrals

**Technical Architecture Decisions**:

- Justify frontend framework choice (e.g. Next.js App Router when selected)  
- Justify UI approach for the recorded human–system interaction  
- Define runtime communication that implements the Pattern Decision  
- Specify streaming vs non-streaming requirements

### 2. Application Runtime Specification

Implement the recorded Pattern Decision. Name runtime roles only when that decision requires them. Do not invent a default crew of 3–4 agents.

**Runtime roles** (when the pattern uses more than one model call):

- Role, goal, and tools (least privilege)  
- Memory / session requirements (default: none or short-lived for reproducibility)

**Task / Turn Orchestration**:

- Dependencies and execution flow matching the chosen pattern  
- Expected outputs and data formats  
- Context passing between steps  
- Error handling, retries, cancellation / timeout behavior  
- Performance budgets (max execution time, token / turn limits)

**Runtime-Conditional Configuration** (fill the subsection matching Selected Runtime):

- **crewai**: composition and process type that implement the recorded pattern, YAML agent/task config, `max_iter`, task context chaining  
- **claude-agent-sdk**: coordinator + `AgentDefinition` specialists only when the pattern is agent, hooks, `allowed_tools`, session policy  
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

- Primary endpoint contract: request schema, response schema, streaming/event envelope  
- Validation, rate limiting, error envelope shape  
- Alignment with the selected runtime adapter and the recorded pattern

**Data Architecture** (MVP default: none unless PRD requires):

- Explicitly defer persistence when out of MVP; if included, justify minimal store

**Runtime Integration Layer**:

- How the HTTP/API layer invokes the selected runtime  
- Configuration management for the recorded pattern  
- Logging / Prompt Trace hooks per adapter Quality Gates

**Authentication & Secrets**:

- Env-var names only (from `.env.example`); no secret values in artifacts

### 5. DevOps & Deployment Architecture

**CI/CD** (minimal MVP): lint, test, build  
**Hosting**: smallest MVP-appropriate target; health-check endpoint  
**IaC / multi-region / advanced monitoring**: Future Work unless PRD requires  
**Observability**: per-request traces and aggregate dashboards as separate designs

### 6. Data Flow & Integration Architecture

- Request/response path from UI through API to the recorded runtime pattern  
- External tool/API integrations required for MVP only  
- Error propagation and user-visible feedback

### 7. Performance & Scalability Specifications

- Response-time and concurrency targets for MVP at expected volume  
- Scaling path deferred with rationale  
- Token / cost controls at runtime layer

### 8. Security & Compliance Architecture

- AuthN/AuthZ for MVP  
- Encryption and input validation baselines  
- Control Register is the application-layer safety design; `@security.eng` verifies it later  
- Compliance deferred with explicit Open Questions when unknown

### 9. Testing & Quality Assurance Specifications

- Unit, integration, and smoke/acceptance expectations for MVP  
- Runtime-specific checks (task outputs, hook traces, schema validation)  
- Verification checklist (`*verify-change`) before Deliver  
- Security assessment required before Deliver when `security.require_security_assessment` is true

**Evaluation Criteria** (when `*define-eval-criteria` has been run):

Measurable pass criteria across accuracy, latency, safety, security, and cost, derived from PRD KPIs, the SLA, and the consequence of a wrong output — not from what an early prototype happens to score. Ask the operator for thresholds that cannot be derived from inputs; do not invent them.

| ID | Dimension | Metric | Threshold | Grading Method | Source |
|----|-----------|--------|-----------|-----------------|--------|
| EC-001 | Accuracy | … | … | Code-based / LLM judge / Human | PRD §x / Operator answer |

`@qa.eng` implements this table via `*run-evals`, producing the golden dataset, graders, and `evals.md`.

### 10. MVP Launch & Feedback Strategy

- Beta / pilot criteria when applicable  
- Success metrics tied to PRD KPIs  
- Outcome document fields for Deliver (before metric, control, measurement owner)

## Implementation Guidance for AI Development Agents

1. Foundation setup per `setup.md` epic  
2. UX (`ux.md`) when a user-facing surface is in scope  
3. Frontend MVP UI without backend wiring  
4. Backend runtime scaffolding that implements the Pattern Decision  
5. Integration epic wires FE ↔ BE  
6. QA validates unit, integration, smoke, evals, and `*verify-change`  
7. Deliver packages deploy/CI/runbook and the outcome document

## Architecture Validation Checklist

- [ ] PRD requirements mapped to architectural components  
- [ ] Work Ownership, Pattern Decision, Reference Architecture, Model and Context Strategy, and Control Register are complete  
- [ ] Runtime roles exist only when the Pattern Decision requires them  
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

- Timestamp, persona id (`system-arch`), action (`create-sad`, `create-sad --mvp`, `decompose-work`, `select-pattern`, or `define-controls`), resolved `AAMAD_TARGET_RUNTIME`
