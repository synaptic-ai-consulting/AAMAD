---
description: Runtime adapter guidance for building AAMAD-generated MVPs on the Cursor SDK.
globs:
alwaysApply: true
---

# Cursor SDK Adapter Rules

## Purpose
- Define runtime-specific guidance when `AAMAD_TARGET_RUNTIME=cursor-sdk`.
- This adapter governs implementation patterns for generated MVP backends that use Cursor SDK runtime primitives.

## Setup
- Build the runtime with TypeScript and Node.js LTS (pin versions in setup docs for reproducibility).
- Install and lock Cursor SDK dependencies in the generated backend project.
- Configure required runtime environment variables (model/provider keys, gateway/base URL values, and runtime flags used by your organization).
- Record resolved SDK/runtime version, model, temperature, and token or budget controls in artifact Audit sections.

## Mapping
- Model the generated multi-agent backend around explicit runtime roles (coordinator + specialized agents) and document boundaries in SAD/backend.md.
- Keep runtime behaviors contract-first: request schema, response schema, and streaming/event envelopes must be defined before implementation.
- Define tool and subagent surfaces as explicit contracts, including allowed operations and expected return shapes.

## Execution
- Set explicit limits for iteration/turns, tokens, and execution time; avoid implicit defaults.
- Define deterministic retry and idempotency strategy for operations that can be replayed.
- Document cancellation, timeout, and fallback behavior for each runtime-critical path.
- Use runtime sessions/resume only where justified in SAD, and record retention scope in Audit.

## Tools
- Apply least-privilege tool policy per runtime role; do not expose broad tool sets by default.
- Validate MCP server availability/auth before execution; halt with Diagnostic when required servers are unavailable.
- Keep tool input/output contracts JSON-serializable and versioned when consumed across components.
- Restrict high-risk tools (network, shell, write-capable operations) to tasks that explicitly require them.

## Logging
- Capture Prompt Trace and execution diagnostics for runtime actions and tool calls.
- Persist lifecycle logs (tool invocation results, retries, cancellations, errors) under `project-context/2.build/logs`.
- Redact secrets and credentials from trace output and artifact logs.

## Quality Gates
- Enforce schema validation for runtime inputs/outputs before accepting results.
- Validate required artifact headings and output formatting before final write.
- Require citation and grounding checks for analytical outputs when applicable.
- Keep artifact-generation behavior deterministic (low temperature unless justified in Audit).

## Failure Policy
- Halt and write Diagnostic on missing prerequisites, validation failures, unauthorized tools, or unresolved runtime dependencies.
- On budget/context/time overrun, stop execution and document remediation steps and safe retry procedure.
