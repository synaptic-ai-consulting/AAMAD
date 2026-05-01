---
description: Runtime adapter guidance for building AAMAD-generated MVPs on CrewAI.
globs:
alwaysApply: true
---

# CrewAI Adapter Rules

## Purpose
- Define runtime-specific guidance when `AAMAD_TARGET_RUNTIME=crewai`.
- This adapter governs how implementation personas scaffold and validate the generated MVP runtime.

## Setup
- Install CrewAI and dependencies in the generated backend environment.
- Required runtime files should include:
    - `config/agents.yaml`
    - `config/tasks.yaml`
    - `crew.py` (or equivalent runtime entrypoint)
- Load secrets from environment variables and provide names in `.env.example`.
- Record resolved `llm`, temperature, and max token controls in Audit.

## Mapping
- All CrewAI agent and task definitions MUST be externalized to YAML files under a config/ directory (e.g., config/agents.yaml, config/tasks.yaml).
- Use explicit task context chaining (`Task.context`) for deterministic dependency flow.
- Define `expected_output` with required headings and target artifact paths.
- Prefer `allow_delegation=false` unless the SAD justifies delegated manager patterns.

## Execution
- Prefer sequential process mode for reproducible MVP builds.
- Use hierarchical process mode only when justified in SAD and documented in Audit.
- Baseline controls:
    - `max_iter <= 12` for MVP tasks unless explicitly justified.
    - `max_execution_time` tuned per epic.
    - `max_retry_limit >= 2`.
    - `max_rpm` set at crew level for budget stability.
- If using function-calling agents, do not switch mode mid-run; record chosen mode in Audit.
- Use `kickoff_for_each` only for truly independent batch items and document deterministic merge keys.

## Tools
- Bind only the minimum required tool set per agent/task.
- Validate YAML-referenced tools before kickoff to avoid runtime binding errors.
- Keep tool configs JSON-serializable; load secret parameters via env vars.
- Permit web/API tools only where explicitly justified by persona scope.

## Logging
- Capture rendered system/user prompts in Prompt Trace before execution.
- Record lifecycle events (task start/stop, retries, guardrail outcomes) in Trace Log.
- Keep Prompt Trace and Trace Log in project-context artifacts, not inline with generated code.
- If using step callbacks/event listeners, redact secrets and persist logs under `project-context/2.build/logs`.

## Quality Gates
- Validate required template headings before final artifact write.
- Use `Task.guardrail` for high-risk outputs (schema limits, content rules, size checks).
- Require `Task.id` and explicit output path for traceability.
- For machine-ingested output sections, enforce plain markdown/JSON without code fences.
- For high-risk outputs, require a human review gate (`human_input=true` or explicit review task).

## Failure Policy
- On missing runtime prerequisites, unresolved tools, heading mismatches, or guardrail failure: halt and write Diagnostic.
- On context overflow or budget breach: halt and report remediation notes in the artifact.

## Memory
- Default memory=False for reproducibility; if memory=True, constrain to current epic, redact secrets, and persist logs to project-context/2.build/logs.
- If memory=True, set `CREWAI_STORAGE_DIR` to a project-scoped path and record scope/retention in Audit.