---
name: run-evals
description: Defines and runs an evaluation strategy for an AAMAD project — golden dataset, code-based checks, LLM-as-judge scoring, and production monitoring recommendations for DevOps. Use when the operator invokes *run-evals, asks to build an eval suite, test LLM/agent quality, or define acceptance criteria for a multi-agent system before deploy.
disable-model-invocation: true
---

# Run Evals

Define and implement the evaluation strategy for the current AAMAD project, then write `project-context/2.build/evals.md`. Owned by `@qa.eng`; invoked as `*run-evals`.

For grading-ladder detail, judge calibration, a worked example, and anti-patterns to avoid, see [reference.md](reference.md).

## Step 1: Load context

Read, in order:
- `project-context/1.define/prd.md`, `sad.md`, `system-description.md` (if present), `project-context/1.define/user-stories/*.md`
- `project-context/2.build/backend.md`, `integration.md`
- `aamad.config.yml` (if present); resolve `AAMAD_TARGET_RUNTIME`

If `sad.md` section "9. Testing & Quality Assurance Specifications" already contains an evaluation criteria table (dimension, metric, threshold, grading method, source), treat it as the contract to implement — do not re-derive thresholds it already settles. Most projects built before this capability existed will not have this table; that is expected, not an error.

## Step 2: Gap check — ask the operator

Business context an eval suite needs is frequently absent from `project-context/`. Do not invent thresholds, SLAs, or risk tolerance — per `aamad-core.mdc`, on missing or ambiguous inputs, write Assumptions and Open Questions rather than fabricate content.

Check for these six items. Skip any already answered by the SAD criteria table or another loaded artifact:

1. Accuracy threshold — what counts as a passing answer
2. Latency target (p95) and cost ceiling per request
3. Consequence of a wrong output — sets the required confidence level
4. Regulatory/safety constraints and any action the system must never take
5. Representative input distribution and where golden data comes from (real logs vs. synthetic)
6. Whether a human-labeled set exists for judge calibration, and which model may act as judge

If any remain unanswered, ask in a **single batched round** — do not interrogate one at a time. Each question offers 3–5 concrete options as usable values (not abstract labels) plus an escape hatch:

- Good option: "p95 under 2s — interactive chat"
- Bad option: "Low latency"
- Always include an escape hatch: "No target defined yet — use a placeholder and flag under Open Questions"

Where the `AskQuestion` tool is available, use it so options render as selectable choices in the chat window. Where it is not available, present the same questions as a short numbered list in the response and wait for the operator's reply before continuing.

Record each answer in `evals.md` under **Assumptions**, attributed to the operator. For anything the operator declines to specify, use the escape-hatch value and record it under **Open Questions** instead of blocking.

## Step 3: Derive success criteria

For each behavior in scope, turn a vague requirement into a measurable one:

1. **Name the behavior specifically** — "summarize claims accurately" becomes "extract claimant name, policy number, and loss amount with 100% field accuracy."
2. **Set the threshold from the SLA and cost-of-wrong-answer**, not from whatever the current build happens to score.
3. **Enumerate failure modes** as dataset categories (e.g. missing field, wrong-claim leakage, malformed output).
4. **Include adversarial and edge-case inputs** — a golden dataset of only clean inputs will not predict production performance.

Cover five dimensions at minimum: accuracy, latency, safety, security, cost. See [reference.md](reference.md) for a fully worked example across these five.

## Step 4: Select grading methods (the ladder)

Climb only as high as the behavior requires:

| Method | Use for | Cost |
|---|---|---|
| **Code-based** | Schema validation, exact/regex match, length, presence checks, numeric comparisons — anything unambiguous | Milliseconds, near-zero |
| **LLM-as-judge** | Tone, reasoning quality, faithfulness, edge-case appropriateness — anything requiring interpretation | One API call per item |
| **Human review** | High-stakes or novel behavior neither code nor a calibrated judge can be trusted on | Slow, expensive, sample only |

Rules:
- Default to code-based wherever the behavior allows it.
- Grade with a judge model **different** from the model under test, to avoid self-preference.
- Use constrained verdicts (a small fixed label set) over free-form scores.
- **Calibrate the judge** against human-labeled examples before trusting its verdicts — an uncalibrated judge produces confident scores that may not be trustworthy, which is worse than no automated grade.

## Step 5: Build the suite

In the target project, create:
- `evals/dataset/*.jsonl` — golden dataset, one file per failure-mode category from Step 3
- `evals/checks/` — code-based check functions
- `evals/judge/` — judge prompt(s) and rubric, if any dimension needs one
- `evals/run.py` (or runtime-appropriate equivalent) — runner that executes the dataset against the system and produces per-item pass/fail or score

### Runtime instrumentation

Instrument per the active `AAMAD_TARGET_RUNTIME` adapter rule so the eval runner and later production monitoring share the same trace data:

- **`crewai`** — use step callbacks / event listeners for task start/stop, retries, and guardrail outcomes; persist logs under `project-context/2.build/logs` per `adapter-crewai.mdc`.
- **`claude-agent-sdk`** — use `PreToolUse`, `PostToolUse`, `SubagentStart`, `SubagentStop` hooks to capture lifecycle events; persist under `project-context/2.build/logs` per `adapter-claude-agent-sdk.mdc`.
- **`cursor-sdk`** — capture Prompt Trace and per-tool-call diagnostics; persist lifecycle logs under `project-context/2.build/logs` per `adapter-cursor-sdk.mdc`.

Redact secrets from all trace output, matching each adapter's Logging section.

## Step 6: Execute and interpret

- Run the full suite; record a per-category breakdown, not just a mean — an aggregate score can look healthy while a specific category is failing.
- Report calibration evidence for any judge in use (agreement rate against the human-labeled sample).
- Flag any dimension without a passing result as a Deliver blocker or an explicit accepted gap.

## Step 7: Write evals.md

Fill `.cursor/templates/evals-template.md` and write to `project-context/2.build/evals.md`. Include:
- The Success Criteria table with a `Source` column tracing each threshold to a PRD/SAD anchor or an operator answer from Step 2.
- **Production Monitoring Recommendations** — the explicit handoff to `@devops.eng` for Deliver:
  - Request-level trace fields: model/version, input/output token counts, latency, stop reason, tool calls
  - Dashboard metrics: cost per request, latency p50/p95, task success rate, error rate by type
  - Threshold alerts: e.g. cost spike over 150% of 7-day average, latency p95 crossing SLA
  - Change attribution: distinguish model drift, data drift, and model-update effects so the right fix is applied
  - Business-KPI translation: map the technical metrics above to the business metric they drive (e.g. task success rate → first-contact resolution)
- Append an Audit entry: timestamp, persona id (`qa-eng`), action (`run-evals`), resolved `AAMAD_TARGET_RUNTIME`.

## Adopting evals in an existing project

If `sad.md` has no criteria table because the project reached QA before this capability existed, run this skill directly — Step 2's gap check supplies what the SAD would otherwise have settled. Be deliberate that the resulting dataset does not just confirm current behavior: source items from the PRD and user stories, and include inputs the implementation was never exercised against (see the contract-review postmortem in [reference.md](reference.md)). Once `evals.md` has agreed thresholds, ask `@system.arch` to fold them back into SAD section 9 so future changes have a real gate. `*sync-docs` does not edit Define artifacts.
