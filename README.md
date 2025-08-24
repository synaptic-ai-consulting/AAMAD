# AAMAD – AI-Assisted Multi-Agent Application Development Framework

**AAMAD** is an open, production-grade framework for building, deploying, and evolving multi-agent applications using best context engineering practices.  
It systematizes research-driven planning, modular AI agent workflows, and rapid MVP/devops pipelines for enterprise-ready AI solutions.

---

## Table of Contents

- [What is AAMAD?](#what-is-aamad)
- [Repository Structure](#repository-structure)
- [How to Use the Framework](#how-to-use-the-framework)
- [Phase 2: Build Workflow (Multi-Agent)](#phase-2-build-workflow-multi-agent)
- [Core Concepts](#core-concepts)
- [Contributing](#contributing)
- [License](#license)

---

## What is AAMAD?

AAMAD is based on the latest research in AI-assisted, multi-agent system development and CrewAI methodologies.  
It enables teams to:

- Launch projects with autonomous or collaborative AI agents
- Rapidly prototype MVPs with clear context boundaries
- Use production-ready architecture/design patterns
- Accelerate delivery, reduce manual overhead, and enable continuous iteration

---

## Repository Structure

    aamad/
    ├─ .cursor/
    │ ├─ agents/ # Agent persona markdown files (definitions & actions)
    │ ├─ prompts/ # Parameterized and phase-specific agent prompts
    │ ├─ rules/ # Architecture, workflow, and epics rules/patterns
    │ ├─ templates/ # Generation templates for research, PRD, SAD, etc.
    │ ├─ personas.md # List of all active personas (index)
    │ ├─ epics.md # Mapping of epics to personas, artifacts, actions
    ├─ project-context/
    │ ├─ 1.define/ # Project-specific PRD, SAD, research reports, etc.
    │ ├─ 2.build/ # Output artifacts for setup, frontend, backend, etc.
    │ ├─ 3.deliver/ # QA logs, deploy configs, release notes, etc.
    ├─ CHECKLIST.md # Step-by-step Phase 2 execution guide
    ├─ README.md # This file


**Framework artifacts** (in `.cursor/`) are reusable for any new project.  
**Project-context** contains all generated and instance-specific documentation for each app built with AAMAD.

---

## How to Use the Framework

1. **Clone this repository.**
2. In `project-context/1.define`, add or generate your PRD and SAD using provided templates.
3. Confirm `.cursor/` contains the full agent, prompt, and rule set.
4. Follow the `CHECKLIST.md` to run Phase 2 (build) using multi-agent autonomy—typically, via CursorAI or another agent platform.
5. Each agent persona executes its epic(s), producing separate markdown artifacts and code as they go.
6. Review, test, and launch the MVP, then iterate or scale with additional features.

---

## Phase 2: Build Workflow (Multi-Agent)

Each role is embodied by an agent persona, defined in `.cursor/agents/`.  
Phase 2 is executed by running each epic in parallel or sequence:

- **Setup:** Scaffold environment, install dependencies, and document (`setup.md`)
- **Frontend:** Build MVP UI + placeholders, document (`frontend.md`)
- **Backend:** Implement CrewAI MVP backend, document (`backend.md`)
- **Integration:** Wire up chat flow, verify, document (`integration.md`)
- **Quality Assurance:** Test end-to-end, log results and limitations (`qa.md`)

Artifacts are versioned and stored in `project-context/2.build` for traceability.

---

## Core Concepts

- **Persona-driven development:** Each workflow is owned and documented by a clear AI agent persona with a single responsibility principle.
- **Context artifacts:** All major actions, decisions, and documentation are stored as markdown artifacts, ensuring explainability and reproducibility.
- **Parallelizable epics:** Big tasks are broken into epics, making development faster and more autonomous while retaining control over quality.
- **Reusability:** Framework reusable for any project—simply drop in your PRD/SAD and let the agents execute.
- **Open, transparent, and community-driven:** All patterns and artifacts are readable, auditable, and extendable.

---

## Contributing

Contributions are welcome!  
- Open an issue for bugs/feature ideas/improvements.
- Submit pull requests with extended templates, new agent personas, or bug fixes.
- Help evolve the knowledge base and documentation for greater adoption.

---

## License

[Insert your chosen open-source license here, e.g., MIT, Apache 2.0, etc.]

---

> For detailed step-by-step Phase 2 execution, see [CHECKLIST.md].  
> For advanced reference and prompt engineering, see `.cursor/templates/` and `.cursor/rules/`.

