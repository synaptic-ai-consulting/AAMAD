# AAMAD Phase 2 Execution Checklist

This checklist guides you step-by-step through running AAMAD Phase 2 (Build), from project setup to MVP delivery, using the agentic workflows defined in the framework.

---

## Before You Start

- [ ] Clone this repository and install all prerequisites (see README.md).
- [ ] Ensure your project-context/1.define folder includes:
  - [ ] product-requirements-document.md (PRD)
  - [ ] market-research-report.md (MR)
- [ ] Confirm `.cursor/` contains:
  - [ ] agents/ (with all persona .md files)
  - [ ] rules/, prompts/, templates/ folders as provided
  - [ ] epics.md and personas.md reference files

---
## Step 0: Architecture Definition (`@system.arch`)

- [ ] Open a Cursor agent chat as `@system.arch`.
- [ ] Run one of:
    - [ ] `*create-sad` — Generate full SAD at project-context/1.define/sad.md using .cursor/templates/sad-template.md.
    - [ ] `*create-sad --mvp` — Generate a lean MVP SAD, deferring nonessential components and NFRs; output to project-context/1.define/sad.md.
- [ ] Validate SAD completeness: stakeholders/concerns, views, quality attributes, decisions, constraints, and risks.
- [ ] Record assumptions and open questions in sad.md for downstream resolution.


## Step 1: Environment Setup (`@project.mgr`)

- [ ] Open a Cursor agent chat as `@project.mgr`
- [ ] Run `*setup-project`
  - [ ] Scaffold directories and install required dependencies
  - [ ] Define environment variables (in .env or as described)
  - [ ] Document all actions in setup.md

---

## Step 2: Frontend Development (`@frontend.eng`)

- [ ] Open a Cursor agent chat as `@frontend.eng`
- [ ] Run `*develop-fe`
  - [ ] Implement MVP chat interface (Next.js, assistant-ui)
  - [ ] Add UI stubs for future planned features
  - [ ] Style and make the interface responsive
  - [ ] Document all decisions and status in frontend.md

---

## Step 3: Backend Development (`@backend.eng`)

- [ ] Open a Cursor agent chat as `@backend.eng`
- [ ] Run `*develop-be`
  - [ ] Scaffold CrewAI backend and MVP crew/agent(s)
  - [ ] Add stub code for future/backlog agent logic
  - [ ] Implement backend chat API endpoint
  - [ ] Document all work in backend.md

---

## Step 4: Integration (`@integration.eng`)

- [ ] Open a Cursor agent chat as `@integration.eng`
- [ ] Run `*integrate-api`
  - [ ] Wire MVP frontend chat to backend chat API
  - [ ] Test basic chat round-trip functionality
  - [ ] Document integration and known issues in integration.md

---

## Step 5: Quality Assurance (`@qa.eng`)

- [ ] Open a Cursor agent chat as `@qa.eng`
- [ ] Run `*qa`
  - [ ] Perform smoke tests and functional tests on chat flow
  - [ ] Verify frontend and backend are connected
  - [ ] Log issues, known gaps, and future work in qa.md

---

## Step 6: Local MVP Launch

- [ ] Follow docs in setup.md and integration.md to run the full MVP locally
- [ ] Confirm MVP chat use case works end-to-end
- [ ] Review all generated artifact files in project-context/2.build

---

## Step 7: Prepare for Next Phase

- [ ] Archive all MVP milestone artifacts in project-context/2.build and 3.deliver
- [ ] List all deferred/backlog features in qa.md and/or as GitHub issues
- [ ] Share repo and context docs with team or community for feedback

---

> For detailed guidelines and troubleshooting, see README.md and documentation in `.cursor/templates` and `.cursor/rules`.


