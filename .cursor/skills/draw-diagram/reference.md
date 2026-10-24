# Who draws what

This is the default tool when a persona's document needs a diagram. Draw only the types on that persona's row. Content comes from that persona's declared inputs.

| Persona | Types | Inputs the figure may use |
|---|---|---|
| `@product-mgr` | journey, story-map, quadrant | `system-description.md`, `prd.md`, `mrd.md`, user stories |
| `@system.arch` | architecture, architecture-delta, it-state, nested, layers, dependency, high-level, deployment, er | Review artifacts, `sad.md`, `sfs/`, `prd.md` |
| `@project.mgr` | high-level, timeline | `prd.md`, `sad.md`, `setup.md` |
| `@frontend.eng` | flowchart, journey | `prd.md`, `sad.md`, `frontend.md` |
| `@backend.eng` | sequence, state, er, db-schema | `prd.md`, `sad.md`, `backend.md` |
| `@integration.eng` | sequence, swimlane, data-flow, process | `prd.md`, `frontend.md`, `backend.md`, `integration.md` |
| `@qa.eng` | flowchart, sequence | `qa.md`, `prd.md`, `sad.md` |
| `@security.eng` | architecture, deployment | `security.md`, `sad.md`, `prd.md`, build docs |
| `@devops.eng` | deployment, gantt | `deploy.md`, `sad.md`, `user-guide.md` |

Type references are `vendor/diagram-design/references/type-<name>.md`. Architecture containment (dashed administrative bands, solid traffic boxes) is a variant inside `type-architecture.md`, not a separate type.

## Parent-doc link

| Parent file | SVG link |
|---|---|
| `project-context/0.review/*.md` | `../diagrams/<persona-id>/<slug>.svg` |
| `project-context/1.define/*.md` | `../diagrams/<persona-id>/<slug>.svg` |
| `project-context/1.define/sfs/*.md` | `../../diagrams/<persona-id>/<slug>.svg` |
| `project-context/2.build/*.md` | `../diagrams/<persona-id>/<slug>.svg` |
| `project-context/3.deliver/*.md` | `../diagrams/<persona-id>/<slug>.svg` |
