# AAMAD Framework: IDE Gap Analysis & Migration Guide

## Cursor vs Claude Code vs VS Code \+ GitHub Copilot

---

## 1\. Executive Summary

AAMAD (AI-Assisted Multi-Agent Application Development) is a context engineering framework built around Cursor IDE's specific artifact system: `.cursor/rules/*.mdc`, `.cursor/agents/`, `.cursor/prompts/`, and `.cursor/templates/`. This document analyzes the feasibility of running AAMAD in **Claude Code** and **VS Code \+ GitHub Copilot**, identifies feature gaps, and provides concrete migration paths including required framework extensions.

**Bottom line**: Both alternative IDEs can support AAMAD's core workflow, but each requires a different translation layer. Claude Code is the closest match architecturally and requires the least adaptation. VS Code \+ GitHub Copilot requires more structural changes but offers the broadest model flexibility.

---

## 2\. AAMAD Architecture Recap

### Core Artifacts (Cursor-Specific)

| Artifact | Location | Purpose |
| :---- | :---- | :---- |
| Rules (`.mdc`) | `.cursor/rules/` | Always-on context rules with YAML frontmatter (`description`, `globs`, `alwaysApply`) |
| Agent Personas | `.cursor/agents/*.md` | Role definitions (PM, Architect, FE, BE, QA, etc.) with YAML frontmatter |
| Prompts | `.cursor/prompts/` | Phase-specific prompt templates |
| Templates | `.cursor/templates/` | PRD, SAD, MR document templates |
| Project Context | `project-context/` | Phase-gated output directories (1.define, 2.build, 3.deliver) |
| CLI Installer | `pip install aamad` | Extracts `.cursor/` bundle into project |

### Key Cursor Features AAMAD Relies On

1. **`.mdc` rules with `alwaysApply: true`** — Rules auto-inject into every agent conversation  
2. **`@agent` mentions** — Invoke specific personas (e.g., `@backend.eng`) in chat  
3. **Glob-based rule scoping** — Conditional rule application based on file patterns  
4. **Fresh chat sessions** — Context management via `Cmd+Shift+P → "New Chat"`  
5. **Agent-requested rules** — AI can choose to include rules based on `description` field

---

## 3\. Feature-by-Feature Gap Analysis

### 3.1 Rules / Instructions System

| Feature | Cursor | Claude Code | VS Code \+ Copilot |
| :---- | :---- | :---- | :---- |
| **Always-on rules** | `.cursor/rules/*.mdc` with `alwaysApply: true` | `CLAUDE.md` / `.claude/CLAUDE.md` | `.github/copilot-instructions.md`, `AGENTS.md` |
| **File format** | `.mdc` (YAML frontmatter \+ markdown body) | `.md` (plain markdown, no frontmatter) | `.instructions.md` (YAML frontmatter \+ markdown body) |
| **Glob-based scoping** | `globs:` field in `.mdc` frontmatter | ❌ Not supported natively | `applyTo:` field in `.instructions.md` frontmatter |
| **Multiple rule files** | ✅ Multiple `.mdc` files in `rules/` | ❌ Single `CLAUDE.md` for always-on; `.claude/rules/` for extra | ✅ Multiple `.instructions.md` files |
| **Auto-injection** | Per-file and always-on modes | Always-on via `CLAUDE.md` only | Per-file via `applyTo` patterns |
| **AI-requested loading** | Agent can request rules based on `description` | ❌ Must be explicit or always-on | ✅ Agent can match based on `description` in frontmatter |
| **Cross-IDE compatibility** | Cursor only | Claude Code \+ VS Code (detects `.claude/` folder) | VS Code also detects `.claude/rules/` and `CLAUDE.md` |

**Gap Impact (Claude Code)**: 🔴 **HIGH** — AAMAD uses 5 separate `.mdc` rule files (`aamad-core`, `development-workflow`, `adapter-crewai`, `adapter-registry`, `epics-index`) that all auto-apply. Claude Code's `CLAUDE.md` is a single file, so all rules must be consolidated or a workaround implemented.

**Gap Impact (VS Code \+ Copilot)**: 🟡 **MEDIUM** — The `.instructions.md` format supports glob patterns and multi-file organization, making it a closer match. However, the frontmatter schema differs (`applyTo` vs `globs`, no `alwaysApply` boolean — `applyTo: "**"` serves as equivalent).

---

### 3.2 Agent Personas

| Feature | Cursor | Claude Code | VS Code \+ Copilot |
| :---- | :---- | :---- | :---- |
| **Agent definitions** | `.cursor/agents/*.md` with YAML frontmatter | `.claude/agents/*.md` with YAML frontmatter | `.github/agents/*.agent.md` with YAML frontmatter |
| **Invocation** | `@agent-name` mention in chat | Automatic delegation via `description` field; explicit request | Select from agents dropdown; `@agent-name` |
| **Frontmatter fields** | `agent.name`, `id`, `role`, `instructions`, `actions`, `inputs`, `outputs`, `prohibited-actions` | `name`, `description`, `tools`, `disallowedTools`, `model`, `permissionMode`, `maxTurns`, `skills`, `hooks`, `memory` | `name`, `description`, `tools`, `model`, `handoffs`, `agents` (subagents), `target` |
| **Tool restrictions** | Not natively enforced (instructions-based) | ✅ Hard tool allowlist/denylist enforcement | ✅ Tool allowlist in frontmatter |
| **Handoffs between agents** | Manual (user switches chat) | Via subagent chaining or agent teams | ✅ Native `handoffs:` field with button UI |
| **Parallel agents** | Multiple chat tabs | Subagents \+ Agent Teams (experimental) | Subagents (experimental) |

**Gap Impact (Claude Code)**: 🟡 **MEDIUM** — Claude Code's `.claude/agents/` system is structurally very similar but uses different YAML fields. The AAMAD persona schema (with `inputs`, `outputs`, `prohibited-actions`, `actions`) maps well but needs translation. Claude Code adds capabilities AAMAD doesn't have (tool enforcement, model selection, hooks, persistent memory).

**Gap Impact (VS Code \+ Copilot)**: 🟡 **MEDIUM** — VS Code's `.agent.md` format is comparable but again uses different fields. VS Code uniquely supports `handoffs:` for workflow transitions between agents, which maps well to AAMAD's phase-based workflow (Define → Build → Deliver). VS Code also natively detects `.claude/agents/` for cross-compatibility.

---

### 3.3 Context Management & Workflow

| Feature | Cursor | Claude Code | VS Code \+ Copilot |
| :---- | :---- | :---- | :---- |
| **Fresh context per module** | `Cmd+Shift+P → "New Chat"` | `/clear` or start new session | New chat session |
| **File referencing** | `@filename` in chat | `@path/to/file` in prompt | `#file:path/to/file` or drag-and-drop |
| **Context window management** | Manual session management | Auto-compaction at \~95% capacity | Automatic context management |
| **Plan mode** | Not native | ✅ `Shift+Tab` for plan-then-execute | ✅ "Plan" agent with read-only tools |
| **Background tasks** | ❌ | ✅ `Ctrl+B` to background tasks | ✅ Cloud/background agents |
| **MCP server support** | ✅ | ✅ via `.mcp.json` | ✅ via settings or `.vscode/mcp.json` |

**Gap Impact**: 🟢 **LOW** — All three IDEs support the fundamental workflow patterns AAMAD requires. The `development-workflow.mdc` rule's guidance about fresh sessions translates directly.

---

### 3.4 CLI Installation

| Feature | Cursor | Claude Code | VS Code \+ Copilot |
| :---- | :---- | :---- | :---- |
| **AAMAD CLI (`aamad init`)** | Extracts to `.cursor/` | ❌ Would need to extract to `.claude/` | ❌ Would need to extract to `.github/` |
| **Bundle format** | ZIP with `.cursor/` structure | N/A | N/A |

**Gap Impact**: 🔴 **HIGH** — The `aamad init` CLI only generates Cursor-format artifacts. A framework extension is required to support alternative output targets.

---

## 4\. Detailed Migration Guide

### 4.1 Migrating AAMAD to Claude Code

#### Step 1: Convert Rules → CLAUDE.md

Since Claude Code uses a single `CLAUDE.md` for always-on project rules, consolidate all 5 `.mdc` files into one master document:

**File: `CLAUDE.md` (project root) or `.claude/CLAUDE.md`**

```
# AAMAD Framework Rules

## Core Rules (from aamad-core.mdc)
[Paste full content of aamad-core.mdc body here]

## Development Workflow (from development-workflow.mdc)
[Paste full content of development-workflow.mdc body here]

## Epics Index (from epics-index.mdc)
[Paste full content of epics-index.mdc body here]

## Adapter Registry (from adapter-registry.mdc)
[Paste full content of adapter-registry.mdc body here]

## CrewAI Adapter (from adapter-crewai.mdc)
[Paste full content of adapter-crewai.mdc body here]
```

**Alternative (recommended for large rule sets)**: Use Claude Code's `.claude/rules/` directory with individual markdown files. VS Code will also detect these:

```
.claude/
├── CLAUDE.md                    # Summary + cross-references
├── rules/
│   ├── aamad-core.md
│   ├── development-workflow.md
│   ├── adapter-crewai.md
│   ├── adapter-registry.md
│   └── epics-index.md
```

⚠️ **Limitation**: `.claude/rules/` files in Claude Code CLI do not support glob-based conditional application. All rules are loaded at session start. This is functionally equivalent to `alwaysApply: true` in Cursor, which is what AAMAD uses for all its rules anyway — so this is not a practical limitation for AAMAD specifically.

#### Step 2: Convert Agent Personas → Claude Code Subagents

Translate each `.cursor/agents/*.md` file to `.claude/agents/*.md`:

**Cursor format (`.cursor/agents/backend-eng.md`):**

```
---
agent:
  name: Backend Developer
  id: backend-eng
  role: Implements the MVP CrewAI backend, agent(s), and core API.
instructions:
  - Only build CrewAI backend as specified in SAD
  - Load PRD, SAD, and setup.md at start.
actions:
  - develop-be
  - define-agents
inputs:
  - project-context/product-requirements-document.md
  - project-context/system-architecture-doc.md
outputs:
  - project-context/2.build/backend.md
prohibited-actions:
  - Implement persistent storage
  - Work outside MVP scope
---
```

**Claude Code format (`.claude/agents/backend-eng.md`):**

```
---
name: backend-eng
description: Implements the MVP CrewAI backend, agents, and core API. Use when building backend components per SAD specification. Delegate backend development tasks to this agent.
tools: Read, Edit, Write, Bash, Grep, Glob
disallowedTools: WebFetch
model: inherit
---

# Backend Developer (@backend.eng)

You own the CrewAI backend and agent scaffolding for MVP.

## Constraints
- Only build CrewAI backend as specified in SAD (no database, no integrations, no analytics)
- Load PRD, SAD, and setup.md at start from project-context/
- Output actions, files, and summaries ONLY to project-context/2.build/backend.md
- Halt and report if requested to build non-MVP/backlog features

## Supported Commands
- `*develop-be` — Scaffold CrewAI backend
- `*define-agents` — Create only the MVP crew/agent YAML/config
- `*implement-endpoint` — Expose chat API for frontend
- `*stub-nonmvp` — Put in stub classes for non-MVP logic
- `*document-backend` — Summarize architecture in backend.md

## Required Inputs
- project-context/product-requirements-document.md
- project-context/system-architecture-doc.md
- project-context/2.build/setup.md

## Output
- project-context/2.build/backend.md

## Prohibited Actions
- Implement persistent storage, analytics, or external integrations
- Work outside MVP scope
- Modify files outside project-context/2.build/
```

Repeat this translation for all 7 agent personas.

#### Step 3: Convert Prompts

The Phase 1 prompt (`prompt-phase-1`) is IDE-agnostic — it works with any AI chatbot. For Claude Code, save it as a skill:

```
.claude/commands/phase-1-define.md
```

This makes it invocable via `/phase-1-define` in Claude Code.

#### Step 4: Settings Configuration

**File: `.claude/settings.json`**

```json
{
  "permissions": {
    "allow": [
      "Bash(python *)",
      "Bash(pip *)",
      "Bash(crewai *)",
      "Bash(npm *)",
      "Bash(npx *)",
      "Read(**)",
      "Edit(**)"
    ]
  },
  "env": {
    "AAMAD_ADAPTER": "crewai"
  }
}
```

#### Step 5: Workflow Adaptation

| AAMAD Workflow Step | Cursor Method | Claude Code Equivalent |
| :---- | :---- | :---- |
| Start fresh context | `Cmd+Shift+P → New Chat` | `/clear` or new terminal session |
| Invoke persona | `@backend.eng tell me about your role` | "Use the backend-eng subagent to tell me about its role" |
| Reference files | `@project-context/prd.md` | `@project-context/prd.md` (same syntax) |
| Parallel work | Multiple chat tabs | Subagents (for focused tasks) or Agent Teams (for coordinated work) |
| Phase transition | Manual persona switch | Subagent chaining or explicit instruction |

---

### 4.2 Migrating AAMAD to VS Code \+ GitHub Copilot

#### Step 1: Convert Rules → Instructions Files

VS Code's `.instructions.md` format is the closest match to Cursor's `.mdc`:

**Directory structure:**

```
.github/
├── copilot-instructions.md          # Always-on summary
├── instructions/
│   ├── aamad-core.instructions.md
│   ├── development-workflow.instructions.md
│   ├── adapter-crewai.instructions.md
│   ├── adapter-registry.instructions.md
│   └── epics-index.instructions.md
```

**Example conversion — `aamad-core.instructions.md`:**

```
---
applyTo: "**"
name: "AAMAD Core Rules"
description: "Core, framework-agnostic rules and contracts for AAMAD; applies to all personas, tasks, and artifacts."
---

## Purpose
- Define universal principles, contracts, and invariants for AI-assisted, multi-agent development.

## Principles
- **Single responsibility personas:** each persona owns a defined epic with explicit inputs, outputs, and prohibited actions.
- **Context-first engineering:** all outputs must trace to PRD, SAD, SFS, or user stories.
[... rest of aamad-core.mdc body ...]
```

**Key mapping:** | Cursor `.mdc` Field | VS Code `.instructions.md` Field | |---------------------|----------------------------------| | `alwaysApply: true` | `applyTo: "**"` | | `globs: ["src/**/*.py"]` | `applyTo: "src/**/*.py"` | | `description:` | `description:` (same) |

#### Step 2: Convert Agent Personas → Custom Agents

Translate each persona to `.github/agents/*.agent.md`:

**VS Code format (`.github/agents/backend-eng.agent.md`):**

```
---
name: Backend Developer
description: Implements the MVP CrewAI backend, agents, and core API per SAD specification.
tools: ['editFiles', 'terminalLastCommand', 'search', 'codebase', 'fetch']
handoffs:
  - label: Run QA Tests
    agent: qa-eng
    prompt: "Run functional and smoke tests for the backend implementation documented in project-context/2.build/backend.md"
    send: false
---

# Backend Developer (@backend.eng)

You own the CrewAI backend and agent scaffolding for MVP.

## Constraints
- Only build CrewAI backend as specified in SAD
- Output to project-context/2.build/backend.md
- Halt if requested to build non-MVP features

## Supported Commands
- `*develop-be` — Scaffold CrewAI backend
- `*define-agents` — Create MVP crew/agent YAML/config
- `*implement-endpoint` — Expose chat API for frontend

## Required Inputs
- project-context/product-requirements-document.md
- project-context/system-architecture-doc.md

## Prohibited Actions
- Implement persistent storage, analytics, or external integrations
- Work outside MVP scope
```

**Unique VS Code advantage — Handoffs**: Define workflow transitions that create buttons in the UI:

```
# In product-mgr.agent.md
handoffs:
  - label: "→ Create Architecture"
    agent: system-arch
    prompt: "Create the SAD using inputs from project-context/1.define/"
    send: false
  
# In system-arch.agent.md  
handoffs:
  - label: "→ Start Build Phase"
    agent: project-mgr
    prompt: "Scaffold the project based on the SAD in project-context/1.define/sad.md"
    send: false
```

This maps perfectly to AAMAD's Define → Build → Deliver flow.

#### Step 3: Convert Prompts

Save Phase 1 prompt as a prompt file:

**File: `.github/prompts/phase-1-define.prompt.md`**

```
---
description: "AAMAD Phase 1: Generate Market Research and Product Requirements Document"
agent: product-mgr
---

[Content from .cursor/prompts/prompt-phase-1]
```

#### Step 4: Required VS Code Extensions

| Extension | Purpose | Required? |
| :---- | :---- | :---- |
| **GitHub Copilot** | Core AI assistant | ✅ Yes |
| **GitHub Copilot Chat** | Agent mode & custom agents | ✅ Yes |
| **Python** (ms-python) | CrewAI development | ✅ Yes |
| **YAML** (redhat) | Agent/config file editing | Recommended |
| **Markdown All in One** | Template editing | Recommended |

#### Step 5: VS Code Settings

**File: `.vscode/settings.json`**

```json
{
  "chat.agent.enabled": true,
  "chat.useAgentsMdFile": true,
  "chat.includeApplyingInstructions": true,
  "chat.includeReferencedInstructions": true,
  "chat.instructionsFilesLocations": [
    ".github/instructions"
  ],
  "chat.agentFilesLocations": [
    ".github/agents"
  ]
}
```

---

## 5\. Required AAMAD Framework Extensions

To officially support Claude Code and VS Code \+ Copilot, the following extensions to the AAMAD framework are recommended:

### 5.1 Multi-IDE CLI Installer

Extend `aamad init` to support target IDE selection:

```shell
# Current (Cursor only)
aamad init

# Proposed extensions
aamad init --ide cursor      # Default, current behavior
aamad init --ide claude-code # Generates .claude/ structure  
aamad init --ide vscode      # Generates .github/ structure
aamad init --ide all         # Generates all three (cross-compatible)
```

**Implementation**: Add a new `--ide` flag to `cli.py` that selects different bundle templates or runs a post-extraction transformation.

### 5.2 Rule Converter Script

A conversion utility to transform `.mdc` rules between formats:

```shell
aamad convert --from cursor --to claude-code
aamad convert --from cursor --to vscode
```

This would handle:

- `.mdc` → `.md` (CLAUDE.md consolidation or `.claude/rules/` split)  
- `.mdc` → `.instructions.md` (frontmatter field mapping)  
- Agent persona YAML field translation

### 5.3 Cross-Compatible Agent Definitions

Create a canonical AAMAD agent schema that includes all fields needed across IDEs, with per-IDE renderers:

```
# .aamad/agents/backend-eng.yaml (canonical)
aamad:
  name: Backend Developer
  id: backend-eng
  role: Implements the MVP CrewAI backend
  inputs: [...]
  outputs: [...]
  prohibited-actions: [...]
  actions: [...]
  
cursor:
  # Cursor-specific overrides
  
claude-code:
  tools: Read, Edit, Write, Bash, Grep, Glob
  model: inherit

vscode:
  tools: ['editFiles', 'terminalLastCommand', 'search']
  handoffs:
    - label: Run QA
      agent: qa-eng
```

### 5.4 AGENTS.md Bridge File

For maximum cross-compatibility, generate an `AGENTS.md` file in the project root. This file is automatically detected by both VS Code \+ Copilot and can be read by Claude Code:

```
# AAMAD Agent Framework

This project uses the AAMAD framework for multi-agent development.
See the full agent definitions in the IDE-specific directories.

## Agent Personas
- **@product-mgr** — Product Manager: Orchestrates product vision and requirements
- **@system.arch** — System Architect: Produces SAD and SFS documents
- **@project.mgr** — Project Manager: Scaffolds project and environment
- **@frontend.eng** — Frontend Developer: Builds MVP chat interface
- **@backend.eng** — Backend Developer: Builds CrewAI backend
- **@integration.eng** — Integration Engineer: Connects frontend and backend
- **@qa.eng** — QA Engineer: Validates MVP functionality

## Workflow
1. **Define** (Phase 1): @product-mgr → Market Research → PRD → @system.arch → SAD
2. **Build** (Phase 2): @project.mgr → @frontend.eng / @backend.eng → @integration.eng → @qa.eng
3. **Deliver** (Phase 3): DevOps deployment

## Rules
All development follows AAMAD core rules. See project-context/ for artifacts.
```

### 5.5 Template & Project-Context Compatibility

The `project-context/` directory structure and `.cursor/templates/` are IDE-agnostic (plain markdown files). These require **no changes** for Claude Code or VS Code. The only adjustment is ensuring agents reference the correct paths in their system prompts.

---

## 6\. Comparison Summary

| Capability | Cursor | Claude Code | VS Code \+ Copilot |
| :---- | :---- | :---- | :---- |
| **AAMAD compatibility** | ✅ Native | 🟡 Needs adaptation | 🟡 Needs adaptation |
| **Rules system** | `.mdc` with full features | `CLAUDE.md` (consolidated) | `.instructions.md` (closest match) |
| **Agent personas** | `.cursor/agents/` | `.claude/agents/` | `.github/agents/` |
| **Glob-based rule scoping** | ✅ Native | ❌ Not available | ✅ via `applyTo:` |
| **Agent tool enforcement** | ❌ Instructions only | ✅ Hard enforcement | ✅ Hard enforcement |
| **Agent handoffs** | ❌ Manual | ❌ Manual / chaining | ✅ Native with UI buttons |
| **Parallel agent work** | Multiple tabs | Subagents \+ Agent Teams | Subagents |
| **Plan mode** | ❌ | ✅ Native | ✅ Via custom agent config |
| **Persistent agent memory** | ❌ | ✅ Native | ❌ |
| **Background tasks** | ❌ | ✅ Native | ✅ Cloud agents |
| **Cross-IDE compatibility** | Cursor only | \+ VS Code detection | \+ Claude format detection |
| **Model flexibility** | Multi-model (Copilot/Claude/etc.) | Claude models only | Multi-model (GPT/Claude/Gemini) |
| **Migration effort** | N/A (native) | Medium (\~2-4 hours) | Medium-High (\~3-5 hours) |
| **Best for** | AAMAD as designed | Solo/power users, CLI-first | Teams, enterprise, model diversity |

---

## 7\. Recommendations for Your Maven Course

### Immediate Actions (Low Effort)

1. **Add an `AGENTS.md` file** to the AAMAD repo root — this is detected by both VS Code and Claude Code, providing a universal "README for agents"  
2. **Document the Phase 1 prompt** as IDE-agnostic — it already works anywhere (Perplexity, ChatGPT, etc.)  
3. **Add a migration guide** section to the AAMAD README linking to specific instructions per IDE

### Short-Term (Framework Extensions)

4. **Extend `aamad init` with `--ide` flag** — generate IDE-appropriate artifact structures  
5. **Create a `scripts/convert_rules.py`** — automated `.mdc` ↔ `CLAUDE.md` ↔ `.instructions.md` conversion  
6. **Add `.claude/agents/` versions** of all personas to the repo alongside `.cursor/agents/`

### Course-Specific Guidance

7. **Cursor students**: Use AAMAD as-is (default path)  
8. **Claude Code students**: Run `aamad init --ide claude-code` (once available) or manually follow Section 4.1 of this guide  
9. **VS Code \+ Copilot students**: Run `aamad init --ide vscode` (once available) or manually follow Section 4.2 of this guide  
10. **All students**: The `project-context/` directory, templates, and CrewAI code are 100% IDE-agnostic — only the rule/agent scaffolding differs

---

## 8\. What Works Without Changes Across All IDEs

- ✅ `project-context/` directory structure and all output artifacts  
- ✅ `.cursor/templates/` (PRD, SAD, MR templates are plain markdown)  
- ✅ Phase 1 prompt (works in any AI chatbot)  
- ✅ CrewAI code, YAML configs, Python source  
- ✅ `pyproject.toml` and dependency management  
- ✅ Git workflow and version control  
- ✅ All business logic and agent orchestration concepts

**What requires IDE-specific adaptation:**

- ⚠️ `.cursor/rules/*.mdc` → `.claude/CLAUDE.md` or `.github/instructions/*.instructions.md`  
- ⚠️ `.cursor/agents/*.md` → `.claude/agents/*.md` or `.github/agents/*.agent.md`  
- ⚠️ `aamad init` CLI bundle extraction target  
- ⚠️ Agent invocation syntax (`@agent` vs natural language delegation vs dropdown selection)

