"""
VS Code / GitHub Copilot IDE conversion logic for AAMAD.

Converts Cursor-format artifacts (.cursor/rules/*.mdc, .cursor/agents/*.md,
.cursor/prompts/, .cursor/skills/, .cursor/templates/) into VS Code / Copilot
format (.github/instructions/*.instructions.md, .github/agents/*.agent.md,
.github/prompts/, .github/templates/, .vscode/settings.json).
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any

# Rule order (same as Claude Code; dependency order)
RULE_ORDER = [
    "aamad-core",
    "conciseness",
    "development-workflow",
    "brownfield-review",
    "epics-index",
    "delivery-workflow",
    "adapter-registry",
    "adapter-crewai",
    "adapter-claude-agent-sdk",
    "adapter-cursor-sdk",
]

# Agent files to convert (exclude dev-crew.md)
AGENT_IDS = [
    "product-mgr",
    "system-arch",
    "project-mgr",
    "frontend-eng",
    "backend-eng",
    "integration-eng",
    "qa-eng",
    "security-eng",
    "devops-eng",
]

# Default Copilot tools (guide §4.2 Step 2)
DEFAULT_TOOLS = ["editFiles", "terminalLastCommand", "search", "codebase", "fetch"]

# Agents that should not have 'fetch' (build personas)
RESTRICT_FETCH_IDS = {
    "backend-eng",
    "frontend-eng",
    "integration-eng",
    "qa-eng",
    "security-eng",
    "project-mgr",
}

# Handoffs for Define → Build → Deliver (agent_id -> list of {label, agent, prompt, send})
HANDOFFS: dict[str, list[dict[str, Any]]] = {
    "product-mgr": [
        {
            "label": "→ Create Architecture",
            "agent": "system-arch",
            "prompt": "Create the SAD using inputs from project-context/1.define/",
            "send": False,
        },
        {
            "label": "→ Start Build Phase (brownfield)",
            "agent": "project-mgr",
            "prompt": "Document and extend the existing project from the approved SAD and constrained PRD. Do not scaffold a replacement app.",
            "send": False,
        },
    ],
    "system-arch": [
        {
            "label": "→ Constrained Define (brownfield)",
            "agent": "product-mgr",
            "prompt": "Write PRD and stories only for the approved enhancements in project-context/1.define/sad.md. Operator Decision must be approved or approved-with-changes.",
            "send": False,
        },
        {
            "label": "→ Start Build Phase",
            "agent": "project-mgr",
            "prompt": "Scaffold the project based on the SAD in project-context/1.define/sad.md",
            "send": False,
        },
    ],
    "project-mgr": [
        {
            "label": "→ Develop Frontend",
            "agent": "frontend-eng",
            "prompt": "Build the MVP chat UI per project-context/2.build/setup.md and SAD.",
            "send": False,
        },
        {
            "label": "→ Develop Backend",
            "agent": "backend-eng",
            "prompt": "Build the selected runtime backend per project-context/2.build/setup.md and SAD.",
            "send": False,
        },
    ],
    "integration-eng": [
        {
            "label": "→ Run QA Tests",
            "agent": "qa-eng",
            "prompt": "Run functional and smoke tests for the implementation in project-context/2.build/.",
            "send": False,
        },
    ],
    "qa-eng": [
        {
            "label": "→ Security Assessment",
            "agent": "security-eng",
            "prompt": "Assess MVP security risks using project-context/2.build/ artifacts and produce security.md.",
            "send": False,
        },
        {
            "label": "→ Deliver MVP",
            "agent": "devops-eng",
            "prompt": "Prepare release and deploy configuration per project-context/2.build/qa.md and SAD.",
            "send": False,
        },
    ],
    "security-eng": [
        {
            "label": "→ Deliver MVP",
            "agent": "devops-eng",
            "prompt": "Prepare release after security.md; note any accepted risks in deploy.md.",
            "send": False,
        },
    ],
}

TEMPLATE_FILES = [
    "aamad-config-template.yml",
    "architecture-backlog-template.md",
    "current-state-template.md",
    "evals-template.md",
    "mrd-template.md",
    "prd-template.md",
    "review-documentation-template.md",
    "sad-brownfield-template.md",
    "sad-template.md",
    "sfs-template.md",
    "system-description-template.md",
    "user-guide-template.md",
    "user-story-template.md",
]


def _parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Split YAML frontmatter and body. Returns (frontmatter_dict, body)."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
    if not match:
        return {}, content.strip()
    try:
        import yaml

        fm = yaml.safe_load(match.group(1)) or {}
    except Exception:
        fm = {}
    body = match.group(2).strip()
    return fm, body


def _rule_apply_to(fm: dict[str, Any]) -> str:
    """Map Cursor alwaysApply/globs to VS Code applyTo."""
    if fm.get("alwaysApply") is True:
        return "**"
    globs = fm.get("globs")
    if not globs:
        return "**"
    if isinstance(globs, list) and len(globs) > 0:
        first = globs[0]
        if first:
            return str(first).strip()
    return "**"


def _rule_display_name(stem: str) -> str:
    """Human-readable rule name from file stem (e.g. aamad-core -> AAMAD Core Rules)."""
    if stem == "aamad-core":
        return "AAMAD Core Rules"
    title = stem.replace("-", " ").title()
    if "adapter" in stem or "workflow" in stem:
        return title + " Rules"
    return title


def _body_to_vscode(body: str) -> str:
    """Rewrite .cursor/rules/ and .cursor/templates/ paths for VS Code."""
    body = re.sub(
        r"\.cursor/rules/([^\s\)\"']+)\.mdc",
        r".github/instructions/\1.instructions.md",
        body,
    )
    body = body.replace(".cursor/rules/", ".github/instructions/")
    return body.replace(".cursor/templates/", ".github/templates/")


def convert_rules(cursor_rules_dir: Path, out_dir: Path) -> list[Path]:
    """
    Convert .cursor/rules/*.mdc to .github/instructions/*.instructions.md.

    Each output file has VS Code frontmatter: applyTo, name, description;
    body is the markdown body from the .mdc (no Cursor frontmatter).
    """
    instructions_dir = out_dir / ".github" / "instructions"
    instructions_dir.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []

    for name in RULE_ORDER:
        mdc_path = cursor_rules_dir / f"{name}.mdc"
        if not mdc_path.exists():
            continue
        text = mdc_path.read_text(encoding="utf-8")
        fm, body = _parse_frontmatter(text)
        apply_to = _rule_apply_to(fm)
        description = fm.get("description") or ""
        display_name = _rule_display_name(name)

        try:
            import yaml

            rule_fm = {
                "applyTo": apply_to,
                "name": display_name,
                "description": description,
            }
            fm_text = yaml.dump(rule_fm, default_flow_style=False, allow_unicode=True, sort_keys=False)
        except Exception:
            fm_text = f'applyTo: "{apply_to}"\nname: "{display_name}"\ndescription: "{description}"\n'
        content = "---\n" + fm_text.strip() + "\n---\n\n" + _body_to_vscode(body)
        out_path = instructions_dir / f"{name}.instructions.md"
        out_path.write_text(content, encoding="utf-8")
        created.append(out_path)

    return created


def _get_agent_id(fm: dict, filename_stem: str) -> str:
    """Extract agent id from frontmatter or filename."""
    agent = fm.get("agent") or {}
    if isinstance(agent, dict) and agent.get("id"):
        return str(agent["id"])
    return filename_stem


def _get_agent_name(fm: dict) -> str:
    """Extract display name from frontmatter."""
    agent = fm.get("agent") or {}
    if isinstance(agent, dict) and agent.get("name"):
        return str(agent["name"])
    return ""


def _get_description(fm: dict) -> str:
    """Build VS Code description from Cursor role + first instruction."""
    agent = fm.get("agent") or {}
    if not isinstance(agent, dict):
        return "AAMAD agent persona."
    role = agent.get("role") or agent.get("primary_objective") or agent.get("mission") or ""
    if role:
        return str(role).strip()
    instructions = fm.get("instructions")
    if isinstance(instructions, list) and instructions:
        first = instructions[0]
        return str(first)[:200].strip() if first else "AAMAD agent persona."
    return "AAMAD agent persona."


def _agent_tools(agent_id: str) -> list[str]:
    """Default tools; restrict fetch for build personas."""
    tools = list(DEFAULT_TOOLS)
    if agent_id in RESTRICT_FETCH_IDS and "fetch" in tools:
        tools = [t for t in tools if t != "fetch"]
    return tools


def convert_agents(cursor_agents_dir: Path, out_dir: Path) -> list[Path]:
    """
    Convert .cursor/agents/*.md to .github/agents/*.agent.md with VS Code frontmatter.

    Skips dev-crew.md. Adds name, description, tools, and optional handoffs.
    """
    agents_dir = out_dir / ".github" / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []

    for agent_id in AGENT_IDS:
        md_path = cursor_agents_dir / f"{agent_id}.md"
        if not md_path.exists():
            continue
        text = md_path.read_text(encoding="utf-8")
        fm, body = _parse_frontmatter(text)

        display_name = _get_agent_name(fm) or agent_id.replace("-", " ").title()
        description = _get_description(fm)
        tools = _agent_tools(agent_id)
        handoffs_list = HANDOFFS.get(agent_id, [])

        # Build YAML frontmatter (VS Code expects name, description, tools, handoffs)
        frontmatter: dict[str, Any] = {
            "name": display_name,
            "description": description,
            "tools": tools,
        }
        if handoffs_list:
            frontmatter["handoffs"] = handoffs_list

        try:
            import yaml

            fm_text = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False)
        except Exception:
            fm_text = f"name: {display_name}\ndescription: {description}\ntools: {tools}\n"
        content = "---\n" + fm_text.strip() + "\n---\n\n" + _body_to_vscode(body)
        out_path = agents_dir / f"{agent_id}.agent.md"
        out_path.write_text(content, encoding="utf-8")
        created.append(out_path)

    return created


PROMPT_SPECS = {
    "prompt-phase-0-review": {
        "out": "phase-0-review.prompt.md",
        "description": "AAMAD Phase 0: Brownfield review of the existing codebase",
        "agent": "system-arch",
    },
    "prompt-phase-1": {
        "out": "phase-1-define.prompt.md",
        "description": "AAMAD Phase 1: Generate Market Research and Product Requirements Document",
        "agent": "product-mgr",
    },
    "prompt-sync-docs": {
        "out": "sync-docs.prompt.md",
        "description": "AAMAD: After a code change, propose descriptive-doc updates and wait for operator approval",
        "agent": None,
    },
}


def convert_prompts(cursor_prompts_dir: Path, out_dir: Path) -> list[Path]:
    """
    Convert Cursor prompts to .github/prompts/*.prompt.md.

    Adds optional frontmatter (description, agent) per guide §4.2 Step 3.
    """
    prompts_dir = out_dir / ".github" / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)

    created: list[Path] = []
    for src_name, spec in PROMPT_SPECS.items():
        prompt_path = cursor_prompts_dir / src_name
        if not prompt_path.exists():
            continue
        body = _body_to_vscode(prompt_path.read_text(encoding="utf-8"))
        frontmatter_lines = [
            "---",
            f'description: "{spec["description"]}"',
        ]
        if spec.get("agent"):
            frontmatter_lines.append(f"agent: {spec['agent']}")
        frontmatter_lines.extend(["---", ""])
        content = "\n".join(frontmatter_lines) + body
        out_path = prompts_dir / spec["out"]
        out_path.write_text(content, encoding="utf-8")
        created.append(out_path)
    return created


# Copilot has no skills primitive; convert Cursor skills to prompt files
# bound to the owning agent instead.
SKILL_PROMPT_SPECS = {
    "run-evals": {
        "out": "run-evals.prompt.md",
        "description": "AAMAD: Define and run the evaluation strategy (golden dataset, code-based checks, LLM-as-judge, production monitoring recommendations)",
        "agent": "qa-eng",
    },
    "draw-diagram": {
        "out": "draw-diagram.prompt.md",
        "description": "AAMAD: Publish an editorial HTML + SVG figure for the current persona",
        "agent": None,
    },
    "sync-docs": {
        "out": "sync-docs.prompt.md",
        "description": "AAMAD: After a code change, propose descriptive-doc updates and wait for operator approval",
        "agent": None,
    },
}


def convert_skills(cursor_skills_dir: Path, out_dir: Path) -> list[Path]:
    """
    Convert Cursor skills (.cursor/skills/<name>/SKILL.md) to VS Code Copilot
    prompt files (.github/prompts/*.prompt.md) bound to the owning agent,
    since Copilot has no skills primitive. Body is copied from SKILL.md with
    its own frontmatter stripped and replaced.
    """
    prompts_dir = out_dir / ".github" / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)

    created: list[Path] = []
    skills_root = out_dir / ".github" / "skills"
    for skill_name, spec in SKILL_PROMPT_SPECS.items():
        skill_dir = cursor_skills_dir / skill_name
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        _, body = _parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        body = _body_to_vscode(body)
        frontmatter_lines = [
            "---",
            f'description: "{spec["description"]}"',
        ]
        if spec.get("agent"):
            frontmatter_lines.append(f"agent: {spec['agent']}")
        frontmatter_lines.extend(["---", ""])
        content = "\n".join(frontmatter_lines) + body
        out_path = prompts_dir / spec["out"]
        out_path.write_text(content, encoding="utf-8")
        created.append(out_path)

        dest_skill = skills_root / skill_name
        for file_path in sorted(skill_dir.rglob("*")):
            if file_path.is_dir():
                continue
            rel = file_path.relative_to(skill_dir)
            copied = dest_skill / rel
            copied.parent.mkdir(parents=True, exist_ok=True)
            if file_path.suffix == ".md":
                copied.write_text(
                    _body_to_vscode(file_path.read_text(encoding="utf-8")),
                    encoding="utf-8",
                )
            else:
                shutil.copy2(file_path, copied)
            created.append(copied)
    return created


def convert_templates(cursor_templates_dir: Path, out_dir: Path) -> list[Path]:
    """Copy .cursor/templates/ to .github/templates/, rewriting path references."""
    dest_dir = out_dir / ".github" / "templates"
    created: list[Path] = []
    if not cursor_templates_dir.exists():
        return created
    for file_path in sorted(cursor_templates_dir.rglob("*")):
        if file_path.is_dir():
            continue
        rel = file_path.relative_to(cursor_templates_dir)
        out_path = dest_dir / rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if file_path.suffix in {".md", ".yml", ".yaml"}:
            text = _body_to_vscode(file_path.read_text(encoding="utf-8"))
            out_path.write_text(text, encoding="utf-8")
        else:
            shutil.copy2(file_path, out_path)
        created.append(out_path)
    return created


# Keys we set for AAMAD (merge only these into existing settings)
VSCODE_AAMAD_SETTINGS = {
    "chat.agent.enabled": True,
    "chat.useAgentsMdFile": True,
    "chat.includeApplyingInstructions": True,
    "chat.includeReferencedInstructions": True,
    "chat.instructionsFilesLocations": [".github/instructions"],
    "chat.agentFilesLocations": [".github/agents"],
}


def write_settings(out_dir: Path, *, merge: bool = True) -> Path:
    """
    Write .vscode/settings.json with Copilot chat and AAMAD paths.

    If merge is True and .vscode/settings.json exists, merge only AAMAD-related
    keys so user settings are preserved.
    """
    vscode_dir = out_dir / ".vscode"
    vscode_dir.mkdir(parents=True, exist_ok=True)
    settings_path = vscode_dir / "settings.json"

    if merge and settings_path.exists():
        try:
            data = json.loads(settings_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = {}
        for key, value in VSCODE_AAMAD_SETTINGS.items():
            data[key] = value
    else:
        data = dict(VSCODE_AAMAD_SETTINGS)

    settings_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return settings_path


def get_vscode_planned_paths(dest: Path) -> list[Path]:
    """Return the list of paths that install_vscode_copilot would create (for dry-run)."""
    dest = dest.resolve()
    paths = []
    for name in RULE_ORDER:
        paths.append(dest / ".github" / "instructions" / f"{name}.instructions.md")
    for agent_id in AGENT_IDS:
        paths.append(dest / ".github" / "agents" / f"{agent_id}.agent.md")
    for spec in PROMPT_SPECS.values():
        paths.append(dest / ".github" / "prompts" / spec["out"])
    for spec in SKILL_PROMPT_SPECS.values():
        paths.append(dest / ".github" / "prompts" / spec["out"])
    for name in TEMPLATE_FILES:
        paths.append(dest / ".github" / "templates" / name)
    paths.append(dest / ".vscode" / "settings.json")
    return paths


def install_vscode_copilot(
    cursor_root: Path,
    dest: Path,
    *,
    overwrite: bool = False,
    merge_settings: bool = True,
) -> list[Path]:
    """
    Run full VS Code / Copilot conversion: rules, agents, prompts, settings.

    Args:
        cursor_root: Project root containing .cursor/
        dest: Output directory (usually same as cursor_root)
        overwrite: If False, raise FileExistsError when target dirs already have content
        merge_settings: If True, merge into existing .vscode/settings.json

    Returns:
        List of all created file paths.
    """
    dest = dest.resolve()
    cursor_rules = cursor_root / ".cursor" / "rules"
    cursor_agents = cursor_root / ".cursor" / "agents"
    cursor_prompts = cursor_root / ".cursor" / "prompts"
    cursor_skills = cursor_root / ".cursor" / "skills"
    cursor_templates = cursor_root / ".cursor" / "templates"

    if not cursor_rules.exists():
        raise FileNotFoundError(f"Rules directory not found: {cursor_rules}")

    github_dir = dest / ".github"
    if not overwrite and github_dir.exists():
        existing = list(github_dir.rglob("*"))
        if any(p.is_file() for p in existing):
            raise FileExistsError(
                f"{github_dir} already exists and contains files. Use overwrite=True to replace."
            )

    created: list[Path] = []
    created.extend(convert_rules(cursor_rules, dest))
    if cursor_agents.exists():
        created.extend(convert_agents(cursor_agents, dest))
    if cursor_prompts.exists():
        created.extend(convert_prompts(cursor_prompts, dest))
    if cursor_skills.exists():
        created.extend(convert_skills(cursor_skills, dest))
    if cursor_templates.exists():
        created.extend(convert_templates(cursor_templates, dest))
    settings_path = write_settings(dest, merge=merge_settings)
    created.append(settings_path)

    return created
