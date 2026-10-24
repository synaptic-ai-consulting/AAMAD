# Accessibility baseline

Accessibility is in scope for UI projects. Do not label an interface "accessible" solely because an automated scan passed. Record which automated and manual checks were actually performed in `ux-review.md`.

## Required for the primary task

- The primary task is operable with a keyboard only
- Focus is visible on every interactive control
- Controls have meaningful accessible names (label, `aria-label`, or equivalent)
- Use semantic elements (`button`, `a`, `input`, headings, landmarks) instead of clickable `div`s
- Ordinary text meets WCAG 2.2 AA contrast: 4.5:1 (3:1 for large text), with the documented exceptions
- Pointer targets meet the WCAG 2.2 24-by-24 CSS-pixel minimum, or an equivalent documented exception

## Record, do not assume

In the Mechanical gate of `ux-review.md`:

- Automated checks run (name the tool) or **not tested**
- Manual keyboard pass on the primary task or **not tested**
- Contrast and target-size spot checks or **not tested**

A passing scan with no manual keyboard pass is **not tested** for keyboard operability, not a pass.

## Out of scope unless the PRD asks

Full WCAG conformance audit, assistive-technology lab testing, and performance/load testing stay deferred. Brownfield reviews cover **changed routes and states** unless the approved enhancement is a redesign.
