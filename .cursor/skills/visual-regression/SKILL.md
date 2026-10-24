---
name: visual-regression
description: >-
  Add and run Playwright Test visual snapshots in the generated app. Use when
  capturing, running, or updating UI baselines (*review-ui, *test-visual,
  *update-visual-baselines). A matching snapshot is not proof the design is
  good. First baseline only after Human judgment. Baseline updates wait for
  operator approval.
---

# Visual regression

Repeatable screenshot comparison for UI projects. Playwright Test `toHaveScreenshot` lives in the **generated MVP**, not in the AAMAD installer. Do not add Playwright to AAMAD itself. Do not require Playwright MCP or a Playwright CLI skill.

Invocation: `*review-ui` (first baseline after Human judgment), `*test-visual` / `*qa` (run), `*update-visual-baselines` (operator-approved update).

`@frontend.eng` scaffolds specs and updates snapshots. `@qa.eng` runs the suite. `@ux.designer` does not install Playwright or edit application source.

Read [reference.md](reference.md) for thresholds, fixtures, ignore regions, and the match-is-not-good-design rule.

## When to run

Run when UI is in scope and this turn captures, runs, or updates visual baselines.

Stop if there is no user-facing UI, or `frontend.md` records a no-UI skip. Write **not tested** in `project-context/2.build/ux-review.md` with that rationale.

Brownfield: snapshot **changed** routes and states only.

## Procedure

1. Read `ux.md` viewports, routes, and state matrix (brownfield: changed routes only).
2. If no UI / no-UI skip: record **not tested** in `ux-review.md` and stop.
3. Add Playwright Test as a generated-app **devDependency** for the project stack. Serve any URL the app already uses. Do not assume React. Record the install and script in `setup.md` / `frontend.md`.
4. Write specs that exercise the primary-task states from `ux.md` and call `toHaveScreenshot` per route × state × viewport.
5. **First baseline:** only after `ux-review.md` Human judgment has no open high-severity findings, or the operator accepted them. Commit snapshots next to the spec.
6. **Later runs:** `npx playwright test` or the recorded script. Failures are Mechanical findings; attach the diff path.
7. **Updating a baseline:** present one proposal and **stop**. Do not overwrite snapshots in the same turn. After the operator approves, write only the approved files. Same halt-and-wait pattern as `*sync-docs`.

`*review-ui` may still use the IDE browser to inspect. The **contract** is the Test snapshots.

## Proposal (`*update-visual-baselines`)

Each item names:

- spec path
- snapshot path
- route, state, viewport
- why the UI changed (or that the change is unintentional)

Where `AskQuestion` is available, offer Approve all / Reject all. Partial approval is the operator naming item numbers. Do not continue until they answer.

## Do not

- Treat a green visual run as Human judgment or as proof the original design was good
- Overwrite baselines without operator approval
- Snapshot the whole as-is brownfield app
- Vendor Playwright browsers into the AAMAD repo
- Install Playwright as an AAMAD package dependency
