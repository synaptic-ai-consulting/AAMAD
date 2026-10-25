---
name: verify-change
description: Records a verification checklist for AI-written MVP changes — correctness, security, maintainability, and a short explanation of what shipped, mapped to acceptance-criteria IDs. Use when the operator invokes *verify-change or before recommending security or Deliver.
disable-model-invocation: true
---

# Verify Change

Record that the current change set is understood and checked before Deliver. Owned by `@qa.eng`; invoked as `*verify-change`. Write the checklist into `project-context/2.build/qa.md` (section **Verification checklist**). Do not invent a second QA artifact.

This is not a replacement for `*test-unit`, `*test-integration`, `*test-visual`, `*run-evals`, or `.cursor/skills/product-design/SKILL.md`.

## Step 1: Load context

Read:

- `project-context/1.define/prd.md`, `sad.md`, `user-stories/*.md`, `system-description.md` (if present)
- `project-context/2.build/qa.md`, `frontend.md`, `backend.md`, `integration.md`
- `project-context/2.build/ux-review.md` and `project-context/1.define/ux.md` when UI changed
- `aamad.config.yml` (`quality.require_verification_checklist`, `crew.autonomy`)

## Step 2: Collect the change set

List the files and behaviors this increment shipped. Map each behavior to an acceptance-criteria ID (`AC-*`) when one exists.

## Step 3: Fill the checklist

For the increment, record pass / fail / not applicable with a one-line note:

| Check | Result | AC-* | Note |
|-------|--------|------|------|
| Correctness — unit | | | |
| Correctness — integration / smoke | | | |
| Security — no new secrets; tools stay on the SAD allowlist | | | |
| Maintainability — change stays inside MVP and the recorded pattern | | | |
| Author explanation — what shipped and why it is safe to release | | | |

Rules:

- The author (persona that made the change, summarized here by QA) must explain what shipped in the Author explanation row. A passing test suite is not that explanation.
- When UI changed, cite `ux-review.md` in the note. Do not repeat Shape / Implement / Review / Harden and do not treat a matching visual snapshot as proof the design is good.
- When the Pattern Decision includes a model call, cite `evals.md` status. Do not re-run the eval design here.
- Fail the checklist if an agent loop, live-state retrieval, or a side-effecting tool appeared that the SAD did not allow.

## Step 4: Write qa.md

Add or replace a `### Verification checklist` section in `project-context/2.build/qa.md`. Keep existing Unit / Integration / Smoke sections. Append an Audit entry: timestamp, persona id (`qa-eng`), action (`verify-change`), resolved `AAMAD_TARGET_RUNTIME`.

If `quality.require_verification_checklist` is true (1.0 default) and the Author explanation row is empty, Halt and Report.
