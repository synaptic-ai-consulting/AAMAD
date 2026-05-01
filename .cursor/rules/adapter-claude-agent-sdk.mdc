---
description: Runtime adapter guidance for building AAMAD-generated MVPs on the Claude Agent SDK.
globs:
alwaysApply: true
---

# Claude Agent SDK Adapter Rules

## Purpose
- Define runtime-specific guidance when `AAMAD_TARGET_RUNTIME=claude-agent-sdk`.
- This adapter governs implementation patterns for generated MVP backends that use the Claude Agent SDK.

## Setup
- Install SDK dependencies for the selected language runtime:
    - Python: `pip install claude-agent-sdk`
    - TypeScript: install the Claude Agent SDK package used by your org standard.
- Configure required runtime environment variables (`ANTHROPIC_API_KEY` and any org-specific gateway/base URL settings).
- Record SDK version, resolved model, temperature, and token controls in artifact Audit.

## Mapping
- Represent specialized runtime agents as `AgentDefinition` entries in `ClaudeAgentOptions.agents`.
- Use the main runtime agent as coordinator and invoke specialized agents via the `Agent` tool.
- For cloud-managed multi-agent orchestration, use callable-agent patterns where appropriate and document delegation boundaries in SAD/backend.md.

## Execution
- Set explicit per-task turn and token budgets; do not rely on implicit defaults.
- Use `ClaudeSDKClient` for bidirectional interactive flows and streaming workflows.
- Define retry and idempotency behavior for runtime actions that may be replayed.
- Use session resume/fork only when required, and document rationale and retention scope in Audit.

## Tools
- Default to least-privilege `allowed_tools` lists per runtime task.
- Use built-in tools (`Read`, `Write`, `Edit`, `Bash`, `Glob`, `Grep`, `WebSearch`, `WebFetch`) only where required by scope.
- Prefer in-process MCP servers for custom internal tools; use external MCP servers when process boundaries are required.
- Validate MCP server availability and auth before execution; fail fast with Diagnostic on missing dependencies.

## Logging
- Capture Prompt Trace prior to execution and append to artifacts or trace logs per persona output rules.
- Use hooks (`PreToolUse`, `PostToolUse`, `SubagentStart`, `SubagentStop`) to log lifecycle events and enforce guardrails.
- Persist runtime trace logs under `project-context/2.build/logs` and redact sensitive values.

## Quality Gates
- Enforce structured output contracts using output schema validation or post-write validators.
- Require citation and numeric grounding checks for analytical outputs when applicable.
- Keep artifact-generation tasks deterministic (low temperature unless justified in Audit).
- Validate required headings and machine-ingested formatting before final write.

## Failure Policy
- Halt with Diagnostic when schema validation, guardrails, tool authorization, or runtime prerequisites fail.
- On budget/context overrun, stop execution and write remediation notes in the artifact.
