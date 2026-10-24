"""
Kiro IDE conversion logic for AAMAD.

Converts Cursor-format artifacts (.cursor/rules/*.mdc, .cursor/agents/*.md,
.cursor/prompts/, .cursor/skills/, .cursor/templates/) into Kiro format
(.kiro/steering/, .kiro/agents/, .kiro/skills/, .kiro/templates/).
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Any

import yaml

# Rule order (same as Claude Code / VS Code; dependency order)
RULE_ORDER = [
    "aamad-core",
    "development-workflow",
    "epics-index",
    "delivery-workflow",
    "adapter-registry",
    "adapter-crewai",
    "adapter-claude-agent-sdk",
    "adapter-cursor-sdk",
]

# Agent files to convert (exclude dev-crew.md index; that becomes steering)
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

DEFAULT_TOOLS = ["read", "write", "shell"]
WEB_TOOL_IDS = {"product-mgr", "system-arch"}

STEERING_RESOURCE = "file://.kiro/steering/**/*.md"
SKILL_RESOURCE = "skill://.kiro/skills/**/SKILL.md"

PROMPT_STEERING = {
    "prompt-phase-1": "phase-1-define.md",
    "prompt-sync-docs": "sync-docs.md",
}

TEMPLATE_FILES = [
    "aamad-config-template.yml",
    "evals-template.md",
    "mrd-template.md",
    "prd-template.md",
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
        fm = yaml.safe_load(match.group(1)) or {}
    except Exception:
        fm = {}
    body = match.group(2).strip()
    return fm, body


def _rule_body_to_kiro(body: str) -> str:
    """Rewrite .cursor/rules/ and .cursor/templates/ paths for Kiro."""
    body = re.sub(
        r"\.cursor/rules/([^\s\)\"']+\.)mdc",
        r".kiro/steering/\1md",
        body,
    )
    body = body.replace(".cursor/rules/", ".kiro/steering/")
    return body.replace(".cursor/templates/", ".kiro/templates/")


def _write_steering(
    out_path: Path,
    body: str,
    *,
    inclusion: str,
) -> Path:
    """Write a Kiro steering file with inclusion frontmatter."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    content = f"---\ninclusion: {inclusion}\n---\n\n{body}\n"
    out_path.write_text(content, encoding="utf-8")
    return out_path


def convert_rules(cursor_rules_dir: Path, out_dir: Path) -> list[Path]:
    """
    Convert .cursor/rules/*.mdc to .kiro/steering/<name>.md with inclusion: always.
    """
    steering_dir = out_dir / ".kiro" / "steering"
    created: list[Path] = []

    for name in RULE_ORDER:
        mdc_path = cursor_rules_dir / f"{name}.mdc"
        if not mdc_path.exists():
            continue
        text = mdc_path.read_text(encoding="utf-8")
        _, body = _parse_frontmatter(text)
        body = _rule_body_to_kiro(body)
        created.append(_write_steering(steering_dir / f"{name}.md", body, inclusion="always"))

    return created


def convert_dev_crew_steering(cursor_agents_dir: Path, out_dir: Path) -> list[Path]:
    """Write .cursor/agents/dev-crew.md as always-on steering (roster index)."""
    src = cursor_agents_dir / "dev-crew.md"
    if not src.exists():
        return []
    text = src.read_text(encoding="utf-8")
    _, body = _parse_frontmatter(text)
    body = _rule_body_to_kiro(body)
    out_path = out_dir / ".kiro" / "steering" / "dev-crew.md"
    return [_write_steering(out_path, body, inclusion="always")]


def _get_agent_name(fm: dict) -> str:
    agent = fm.get("agent") or {}
    if isinstance(agent, dict) and agent.get("name"):
        return str(agent["name"])
    return ""


def _get_description(fm: dict) -> str:
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
    tools = list(DEFAULT_TOOLS)
    if agent_id in WEB_TOOL_IDS:
        tools.append("web")
    return tools


def _agent_resources(agent_id: str) -> list[str]:
    resources = [STEERING_RESOURCE]
    if agent_id == "qa-eng":
        resources.append(SKILL_RESOURCE)
    return resources


def convert_agents(cursor_agents_dir: Path, out_dir: Path) -> list[Path]:
    """
    Convert .cursor/agents/*.md to .kiro/agents/<id>.md.

    Skips dev-crew.md. Frontmatter holds name, description, tools, and resources.
    """
    agents_dir = out_dir / ".kiro" / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []

    for agent_id in AGENT_IDS:
        md_path = cursor_agents_dir / f"{agent_id}.md"
        if not md_path.exists():
            continue
        text = md_path.read_text(encoding="utf-8")
        fm, body = _parse_frontmatter(text)

        name = _get_agent_name(fm) or agent_id.replace("-", " ").title()
        frontmatter = {
            "name": name,
            "description": _get_description(fm),
            "tools": _agent_tools(agent_id),
            "resources": _agent_resources(agent_id),
        }
        fm_text = yaml.dump(
            frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False
        )
        content = "---\n" + fm_text.strip() + "\n---\n\n" + _rule_body_to_kiro(body) + "\n"
        out_path = agents_dir / f"{agent_id}.md"
        out_path.write_text(content, encoding="utf-8")
        created.append(out_path)

    return created


def convert_prompts(cursor_prompts_dir: Path, out_dir: Path) -> list[Path]:
    """
    Convert Cursor prompts to manual Kiro steering files (slash-command style).

    Inputs: .cursor/prompts/prompt-*
    Outputs: .kiro/steering/phase-1-define.md, .kiro/steering/sync-docs.md
    """
    steering_dir = out_dir / ".kiro" / "steering"
    created: list[Path] = []
    for src_name, dest_name in PROMPT_STEERING.items():
        prompt_path = cursor_prompts_dir / src_name
        if not prompt_path.exists():
            continue
        body = _rule_body_to_kiro(prompt_path.read_text(encoding="utf-8").strip())
        created.append(
            _write_steering(steering_dir / dest_name, body, inclusion="manual")
        )
    return created


def convert_skills(cursor_skills_dir: Path, out_dir: Path) -> list[Path]:
    """
    Copy .cursor/skills/<name>/ to .kiro/skills/<name>/ (Agent Skills standard).

    Rewrites .cursor/rules/ references inside markdown files.
    """
    kiro_skills = out_dir / ".kiro" / "skills"
    created: list[Path] = []

    if not cursor_skills_dir.exists():
        return created

    for skill_dir in sorted(p for p in cursor_skills_dir.iterdir() if p.is_dir()):
        dest_skill_dir = kiro_skills / skill_dir.name
        for file_path in sorted(skill_dir.rglob("*")):
            if file_path.is_dir():
                continue
            rel = file_path.relative_to(skill_dir)
            out_path = dest_skill_dir / rel
            out_path.parent.mkdir(parents=True, exist_ok=True)
            if file_path.suffix == ".md":
                text = _rule_body_to_kiro(file_path.read_text(encoding="utf-8"))
                out_path.write_text(text, encoding="utf-8")
            else:
                shutil.copy2(file_path, out_path)
            created.append(out_path)

    return created


def convert_templates(cursor_templates_dir: Path, out_dir: Path) -> list[Path]:
    """Copy .cursor/templates/ to .kiro/templates/, rewriting path references."""
    dest_dir = out_dir / ".kiro" / "templates"
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
            text = _rule_body_to_kiro(file_path.read_text(encoding="utf-8"))
            out_path.write_text(text, encoding="utf-8")
        else:
            shutil.copy2(file_path, out_path)
        created.append(out_path)
    return created


def get_kiro_planned_paths(dest: Path) -> list[Path]:
    """Return the list of paths that install_kiro would create (for dry-run)."""
    dest = dest.resolve()
    paths: list[Path] = []
    for name in RULE_ORDER:
        paths.append(dest / ".kiro" / "steering" / f"{name}.md")
    paths.append(dest / ".kiro" / "steering" / "dev-crew.md")
    for dest_name in PROMPT_STEERING.values():
        paths.append(dest / ".kiro" / "steering" / dest_name)
    for agent_id in AGENT_IDS:
        paths.append(dest / ".kiro" / "agents" / f"{agent_id}.md")
    for name in TEMPLATE_FILES:
        paths.append(dest / ".kiro" / "templates" / name)
    return paths


def install_kiro(
    cursor_root: Path,
    dest: Path,
    *,
    overwrite: bool = False,
) -> list[Path]:
    """
    Run full Kiro conversion: steering, agents, skills.

    Args:
        cursor_root: Project root containing .cursor/
        dest: Output directory
        overwrite: If False, raise FileExistsError when .kiro already has files
    """
    dest = dest.resolve()
    cursor_rules = cursor_root / ".cursor" / "rules"
    cursor_agents = cursor_root / ".cursor" / "agents"
    cursor_prompts = cursor_root / ".cursor" / "prompts"
    cursor_skills = cursor_root / ".cursor" / "skills"
    cursor_templates = cursor_root / ".cursor" / "templates"

    if not cursor_rules.exists():
        raise FileNotFoundError(f"Rules directory not found: {cursor_rules}")

    kiro_dir = dest / ".kiro"
    if not overwrite and kiro_dir.exists():
        existing = list(kiro_dir.rglob("*"))
        if any(p.is_file() for p in existing):
            raise FileExistsError(
                f"{kiro_dir} already exists and contains files. Use overwrite=True to replace."
            )

    created: list[Path] = []
    created.extend(convert_rules(cursor_rules, dest))
    if cursor_agents.exists():
        created.extend(convert_dev_crew_steering(cursor_agents, dest))
        created.extend(convert_agents(cursor_agents, dest))
    if cursor_prompts.exists():
        created.extend(convert_prompts(cursor_prompts, dest))
    if cursor_skills.exists():
        created.extend(convert_skills(cursor_skills, dest))
    if cursor_templates.exists():
        created.extend(convert_templates(cursor_templates, dest))
    return created
