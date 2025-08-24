# Agent Personas for AAMAD Phase 2 Development

## @project.mgr - Setup Engineer
- Objective: Prepare development environment and initial project structure.
- Key Tasks:
  - Scaffolding project directories and config files.
  - Installing dependencies per PRD/SAD.
  - Defining environment variables.
  - Documenting all actions in setup.md.

## @frontend.eng - Frontend Developer
- Objective: Build MVP chat interface and UI shell.
- Key Tasks:
  - Implementing basic Next.js chat functionality.
  - Creating visible placeholders for future features.
  - Ensuring MVP UI matches SAD constraints.
  - Documenting decisions and steps in frontend.md.

## @backend.eng - Backend Developer
- Objective: Build MVP CrewAI backend and agent logic.
- Key Tasks:
  - Creating core crew and agents per SAD.
  - Setting up backend endpoints for chat interaction.
  - Stub non-MVP agent features.
  - Documenting implementation in backend.md.

## @integration.eng - Integration Engineer
- Objective: Connect frontend and backend MVP features.
- Key Tasks:
  - Configuring API routing and chat endpoint wiring.
  - Verifying frontend-backend communication using test messages.
  - Documenting steps in integration.md.

## @qa.eng - QA Engineer
- Objective: Validate MVP system functionality.
- Key Tasks:
  - Running functional and smoke tests for MVP features.
  - Logging test coverage, failures, and known gaps in qa.md.
  - Marking “future work” areas for non-functional parts.

