# Visual-regression reference

A matching snapshot means the pixels match an approved baseline. It does not mean the first screenshot was a good design. Human judgment in `ux-review.md` must pass (or the operator must accept remaining high-severity findings) before the first baseline is committed. After that, a diff is a Mechanical finding: fix the UI or ask the operator to accept a new baseline.

## Rendering consistency

- Use the viewport list from `ux.md`
- Use controlled fixture content (realistic labels, empty and error states — not lorem or invented metrics)
- Lock the Playwright browser channel (for example Chromium) and record it in `ux-review.md`
- Prefer the same OS/browser in CI as local capture; document host-font drift if they differ
- Hide or mask dynamic regions (timestamps, request ids, agent tokens, live clocks) with `style` / `mask` / a test-only fixture

## Thresholds

Default to Playwright `toHaveScreenshot` with a small `maxDiffPixels` (or `maxDiffPixelRatio`) so a one-pixel antialias does not fail the suite, and a real layout shift does. Record the chosen values in the spec and in `ux-review.md`. Do not raise the threshold to hide an unreviewed change.

## Spec layout

Prefer a generated-app path the stack already uses for e2e, for example `e2e/visual.spec.ts` plus sibling `*-snapshots/`. One assertion per route × state × viewport. Name snapshots from those three parts.

Record in `setup.md` / `frontend.md`:

- package script (for example `test:visual`)
- command to install browsers (`npx playwright install --with-deps chromium`)
- base URL the spec expects

## Mechanical gate row

In `ux-review.md`, visual regression is `passed` / `failed` / `not tested`, with spec path, snapshot directory, command, browser, and viewports. A failure includes the Playwright diff path. Keep **not tested** distinct from **passed**.

A green visual run is not a Human judgment pass.

## Approval answers (baseline update)

- **Approve all** — write the approved snapshot files
- **Reject all** — leave baselines unchanged; list them under Open Questions on `frontend.md` or `qa.md`
- **Item numbers** — write those snapshots only

If the operator does not answer, leave snapshots unchanged.
