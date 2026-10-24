---
name: sync-docs
description: >-
  After a change set of application source, runtime config, env examples, or
  deploy/CI config, review descriptive project docs, propose the sentences the
  change made false, wait for operator approval, then apply only the approved
  edits. Use when a code-changing AAMAD persona finishes a change set. Does not
  edit PRD, SAD, or Review artifacts.
---

# Sync docs

Closing step for the persona that just changed code. The review is automatic. The write waits for the operator.

Invocation: `*sync-docs`, or the end of any change set of application source, runtime config, env examples, or deploy/CI config.

Owned by the persona the operator invoked. Only `@project.mgr`, `@frontend.eng`, `@backend.eng`, `@integration.eng`, and `@devops.eng` run this skill. `@product-mgr`, `@system.arch`, `@qa.eng`, and `@security.eng` do not.

Read [reference.md](reference.md) for the allowlist, proposal shape, and loop guard.

## When to run

Run this skill **once** after a change set of:

- application source
- runtime or adapter config that the generated app loads
- `.env.example` keys or comments
- deploy or CI config

Do not run it because you just edited this persona's own epic markdown while implementing (for example filling in `backend.md`). Do not run it again because of edits this skill just made.

If this turn only wrote documentation, stop.

## What you may change

Descriptive docs only, and only sentences the change made false. The allowlist is in [reference.md](reference.md).

Define and Review stay authoritative. Do not edit `project-context/1.define/**` or `project-context/0.review/**`. If the code contradicts the PRD, SAD, SFS, or a Review artifact, list that as **spec drift** and do not patch the spec. The operator chooses whether to revert the code or hand the spec change to `@system.arch` or `@product-mgr`.

Do not invent requirements. Do not expand a sentence into a new section. Do not create a `README.md` that does not already exist.

## Procedure

1. Read the files you just changed and every allowlisted doc that exists.
2. Compare stated facts (endpoint, port, env var name, start command, stack, path) to the code.
3. If nothing descriptive is stale, append one Audit line on this persona's own artifact (`Doc sync: no updates`; timestamp, persona id, `sync-docs`) and stop. Do not ask a question.
4. If something is stale, present **one** proposal and **stop**. Do not write the docs in the same turn.
5. After the operator answers, write only the approved items. Append an Audit block (timestamp, persona id, `sync-docs`) on each file touched. Record rejected items under Open Questions on this persona's own artifact.

## Proposal

Group items as **Descriptive updates** or **Spec drift**. Spec-drift items are not editable here.

Each descriptive item names:

- file
- heading
- current sentence
- replacement sentence
- the code path that justifies the replacement

Where the `AskQuestion` tool is available, offer:

- Approve all descriptive updates
- Reject all

Partial approval is the operator naming which item numbers to keep. Where `AskQuestion` is not available, present the same choice as a short numbered list and wait.

Do not continue until the operator answers. If the operator does not answer, leave the docs unchanged.
