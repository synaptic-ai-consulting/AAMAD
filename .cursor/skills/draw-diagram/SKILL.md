---
name: draw-diagram
description: >-
  Default diagram tool for AAMAD personas. Whenever a spec or build document
  needs a diagram (architecture, sequence, flow, state, deployment, data model,
  journey), draw editorial HTML and SVG with the vendored Diagram Design system
  instead of Mermaid, PlantUML, or ASCII art. Writes
  project-context/diagrams/<persona-id>/.
---

# Draw diagram

Default diagram tool for AAMAD personas. Invocation: `*draw-diagram`, or any point in an artifact where a diagram is the right presentation.

The visual system is Diagram Design (MIT, Cathryn Lavery), vendored at `vendor/diagram-design/`. Read [reference.md](reference.md) for which persona may draw which type. Read `vendor/diagram-design/DESIGN.md`, then only the one type reference it selects.

## When to draw

When the document you are writing needs a diagram, draw it with this skill before you finish the artifact. That includes an architecture view, a sequence, a flow, a state machine, a deployment picture, a data model, or a journey.

Do not draw a section that is clearer as prose or a table. Do not add a figure that restates a paragraph without showing structure.

Do not use Mermaid, PlantUML, Graphviz, ASCII art, or another diagram library for a new diagram. Link the exported SVG from the markdown section it illustrates.

Leave an existing `project-context/diagrams/<persona-id>/<slug>.html` alone unless that figure is what you are updating. Edit that file. Do not redraw it from scratch. If a markdown section already contains a Mermaid diagram and you are replacing that figure, remove the Mermaid block and link the SVG. If you are not changing that figure, leave the Mermaid block in place.

## What you may draw

Every box, edge, and label must come from this persona's declared inputs (PRD, SAD, SFS, Review artifacts, or the build doc this persona owns). If a node is not in those inputs, omit it. Record the gap under Assumptions in the parent markdown artifact. Do not invent components to make the picture complete.

Use only a diagram type listed for this persona in [reference.md](reference.md). If the operator asks for a type another persona owns, name that persona and stop.

## Output

Write only:

- `project-context/diagrams/<persona-id>/<slug>.html` — the self-contained diagram
- `project-context/diagrams/<persona-id>/<slug>.svg` — export of the `<svg>`

`<persona-id>` is this persona's id (`system-arch`, `backend-eng`, …). `<slug>` is a short kebab-case name.

In the parent markdown artifact, link the SVG with a path relative to that file, and state the HTML path in one sentence. Append an Audit entry naming both files, the diagram type, and `diagram-design` commit `0b9b10cab3dbf695642fa1a6c4b4f60df9083689`.

## How to draw

1. State the type, the persona, the slug, and what you will leave out.
2. Follow `vendor/diagram-design/DESIGN.md` and the one type reference for layout, connectors, and the accessible SVG contract.
3. Font source is `system`. Omit any Google Fonts `<link>` or `@import`. Do not fetch a website to onboard a brand. Do not change `vendor/diagram-design/references/style-guide.md`.
4. Shell is allowed only for the two commands below. No other shell, and no network.

From the repo root:

```bash
python3 .cursor/skills/draw-diagram/vendor/diagram-design/scripts/export_svg.py \
  project-context/diagrams/<persona-id>/<slug>.html --system-fonts
python3 .cursor/skills/draw-diagram/vendor/diagram-design/scripts/self_check.py \
  --offline project-context/diagrams/<persona-id>/<slug>.html
```

`self_check.py` must print `OK`. If it prints `FAIL`, fix the HTML and run it again.

On Claude Code, Kiro, or VS Code, the same scripts live under `.claude/skills/draw-diagram/`, `.kiro/skills/draw-diagram/`, or `.github/skills/draw-diagram/`.

PNG export needs Playwright. Do not run it unless the operator asks.
