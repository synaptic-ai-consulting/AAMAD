# Sync-docs reference

## Who runs this

| Persona | Own artifact for the no-update Audit line |
|---|---|
| `@project.mgr` | `project-context/2.build/setup.md` |
| `@frontend.eng` | `project-context/2.build/frontend.md` |
| `@backend.eng` | `project-context/2.build/backend.md` |
| `@integration.eng` | `project-context/2.build/integration.md` |
| `@devops.eng` | `project-context/3.deliver/deploy.md` |

`@product-mgr`, `@system.arch`, `@qa.eng`, and `@security.eng` do not run this skill.

## Write allowlist

After operator approval, edit only files that already exist:

- `project-context/2.build/setup.md`
- `project-context/2.build/frontend.md`
- `project-context/2.build/backend.md`
- `project-context/2.build/integration.md`
- `project-context/3.deliver/deploy.md`
- `project-context/3.deliver/user-guide.md`
- generated-app `README.md` (correct it; do not create it)
- comments on keys in `.env.example` (never secret values)

Another persona's file on this list may be edited only when it states a fact the change made false (endpoint, port, env var name, start command, stack, path).

## Do not write

- `project-context/1.define/**`
- `project-context/0.review/**`
- `project-context/2.build/qa.md`, `evals.md`, `security.md`
- application source, tests, or generated runtime config
- `aamad.config.yml`
- diagram HTML/SVG (use `*draw-diagram` if a figure itself is stale)

## Loop guard

A second pass is a new change set of source or config, not a new sentence in a markdown file.

Do not treat these as a trigger:

- the proposal you just wrote in chat
- Audit, Open Questions, or approved replacements this skill just applied
- this persona's own epic markdown updated as part of the same implementation turn

If you cannot name a source or config path from this change set, do not run the skill.

## Proposal shape

```
## Doc sync proposal
Persona: <id>
Change set: <paths>

### Descriptive updates
1. File: <path>
   Heading: <heading>
   Current: <sentence>
   Replacement: <sentence>
   Justified by: <code path>

### Spec drift (not editable here)
1. File: <define or review path>
   Heading: <heading>
   Spec says: <sentence>
   Code does: <sentence>
   Justified by: <code path>
```

Omit an empty group. If both groups are empty, skip the proposal and write `Doc sync: no updates` on the own artifact.

## Approval answers

- **Approve all** — apply every descriptive item.
- **Reject all** — apply none; list them under Open Questions on the own artifact.
- **Item numbers** — apply those items; list the rest under Open Questions.

Spec-drift items stay on the proposal. Do not edit them. Tell the operator the owning persona (`@system.arch` or `@product-mgr`) if they want the spec changed.
