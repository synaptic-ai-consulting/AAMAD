"""
Claude Code IDE conversion logic for AAMAD.

Converts Cursor-format artifacts (.cursor/rules/*.mdc, .cursor/agents/*.md,
.cursor/prompts/, .cursor/skills/, .cursor/templates/) into Claude Code format
(.claude/rules/, .claude/agents/, .claude/commands/, .claude/skills/,
.claude/templates/, .claude/settings.json).
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any

# Rule order for CLAUDE.md summary and split output (dependency order)
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

# Agent files to convert (exclude dev-crew.md index)
AGENT_IDS = [
    "product-mgr",
    "system-arch",
    "ux-designer",
    "project-mgr",
    "frontend-eng",
    "backend-eng",
    "integration-eng",
    "qa-eng",
    "security-eng",
    "devops-eng",
]

# Default tools for Claude Code agents (most personas need these)
DEFAULT_TOOLS = "Read, Edit, Write, Bash, Grep, Glob"

# Agents that should not use WebFetch (build personas)
DISALLOW_WEBFETCH_IDS = {
    "backend-eng",
    "frontend-eng",
    "integration-eng",
    "qa-eng",
    "security-eng",
    "project-mgr",
}


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


def _rule_body_to_claude(body: str) -> str:
    """Rewrite .cursor/rules/ and .cursor/templates/ paths for Claude Code."""
    body = re.sub(
        r"\.cursor/rules/([^\s\)\"']+\.)mdc",
        r".claude/rules/\1md",
        body,
    )
    body = body.replace(".cursor/rules/", ".claude/rules/")
    return body.replace(".cursor/templates/", ".claude/templates/")


def convert_rules(
    cursor_rules_dir: Path,
    out_dir: Path,
    *,
    style: str = "split",
) -> list[Path]:
    """
    Convert .mdc rules to Claude Code format.

    Args:
        cursor_rules_dir: Path to .cursor/rules/
        out_dir: Base output dir (e.g. project root); writes .claude/CLAUDE.md and .claude/rules/
        style: "split" (CLAUDE.md + rules/*.md) or "single" (one CLAUDE.md)

    Returns:
        List of created file paths.
    """
    claude_dir = out_dir / ".claude"
    rules_out = claude_dir / "rules"
    rules_out.mkdir(parents=True, exist_ok=True)

    created: list[Path] = []
    rule_bodies: dict[str, str] = {}

    for name in RULE_ORDER:
        mdc_path = cursor_rules_dir / f"{name}.mdc"
        if not mdc_path.exists():
            continue
        text = mdc_path.read_text(encoding="utf-8")
        _, body = _parse_frontmatter(text)
        body = _rule_body_to_claude(body)
        rule_bodies[name] = body

        if style == "split":
            out_path = rules_out / f"{name}.md"
            out_path.write_text(body, encoding="utf-8")
            created.append(out_path)

    # CLAUDE.md: summary + cross-references for split; full consolidation for single
    claude_md_path = claude_dir / "CLAUDE.md"
    if style == "split":
        lines = [
            "# AAMAD Framework Rules",
            "",
            "This project uses the AAMAD multi-agent development framework.",
            "All rules are loaded from `.claude/rules/`.",
            "",
            "## Rule Files",
        ]
        for name in RULE_ORDER:
            if name in rule_bodies:
                lines.append(f"- [{name}](.claude/rules/{name}.md)")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("For detailed agent/epic/action mapping, see `.claude/rules/epics-index.md`.")
        claude_md_path.write_text("\n".join(lines), encoding="utf-8")
    else:
        sections = []
        for name in RULE_ORDER:
            if name in rule_bodies:
                sections.append(f"## {name.replace('-', ' ').title()}\n\n{rule_bodies[name]}")
        claude_md_path.write_text("\n\n---\n\n".join(sections), encoding="utf-8")

    created.append(claude_md_path)
    return created


def _get_agent_id(fm: dict, filename: str) -> str:
    """Extract agent id from frontmatter or filename."""
    agent = fm.get("agent") or {}
    if isinstance(agent, dict) and agent.get("id"):
        return str(agent["id"])
    return Path(filename).stem


def _get_agent_name(fm: dict) -> str:
    """Extract display name from frontmatter."""
    agent = fm.get("agent") or {}
    if isinstance(agent, dict) and agent.get("name"):
        return str(agent["name"])
    return ""


def _get_description(fm: dict) -> str:
    """Build Claude Code description from Cursor fields."""
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


def _format_instructions(fm: dict) -> str:
    """Format instructions as bullet list for body."""
    instructions = fm.get("instructions")
    if not instructions:
        return ""
    if isinstance(instructions, str):
        return f"- {instructions}"
    if isinstance(instructions, list):
        return "\n".join(f"- {i}" for i in instructions if i)
    return ""


def convert_agents(
    cursor_agents_dir: Path,
    out_dir: Path,
) -> list[Path]:
    """
    Convert .cursor/agents/*.md to .claude/agents/*.md with Claude Code frontmatter.

    Skips dev-crew.md (index file). Converts only files matching AGENT_IDS.
    """
    claude_agents = out_dir / ".claude" / "agents"
    claude_agents.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []

    for agent_id in AGENT_IDS:
        md_path = cursor_agents_dir / f"{agent_id}.md"
        if not md_path.exists():
            continue
        text = md_path.read_text(encoding="utf-8")
        fm, body = _parse_frontmatter(text)

        name = _get_agent_name(fm) or agent_id.replace("-", " ").title()
        description = _get_description(fm)
        tools = DEFAULT_TOOLS
        disallowed = "WebFetch" if agent_id in DISALLOW_WEBFETCH_IDS else ""

        frontmatter_lines = [
            "---",
            f"name: {agent_id}",
            f"description: {description}",
            f"tools: {tools}",
            "model: inherit",
        ]
        if disallowed:
            frontmatter_lines.append(f"disallowedTools: {disallowed}")
        frontmatter_lines.append("---")
        frontmatter_lines.append("")

        new_content = "\n".join(frontmatter_lines) + _rule_body_to_claude(body)
        out_path = claude_agents / f"{agent_id}.md"
        out_path.write_text(new_content, encoding="utf-8")
        created.append(out_path)

    return created


PROMPT_COMMANDS = {
    "prompt-phase-0-review": "phase-0-review.md",
    "prompt-phase-1": "phase-1-define.md",
    "prompt-sync-docs": "sync-docs.md",
}


def convert_prompts(
    cursor_prompts_dir: Path,
    out_dir: Path,
) -> list[Path]:
    """
    Convert Cursor prompts to Claude Code slash commands.

    Inputs: .cursor/prompts/prompt-* (no extension)
    Outputs: .claude/commands/*.md
    """
    claude_commands = out_dir / ".claude" / "commands"
    claude_commands.mkdir(parents=True, exist_ok=True)

    created: list[Path] = []
    for src_name, dest_name in PROMPT_COMMANDS.items():
        prompt_path = cursor_prompts_dir / src_name
        if not prompt_path.exists():
            continue
        out_path = claude_commands / dest_name
        body = _rule_body_to_claude(prompt_path.read_text(encoding="utf-8"))
        out_path.write_text(body, encoding="utf-8")
        created.append(out_path)
    return created


def convert_skills(
    cursor_skills_dir: Path,
    out_dir: Path,
) -> list[Path]:
    """
    Convert Cursor skills to Claude Code skills (native skills path).

    Inputs: .cursor/skills/<skill-name>/ (SKILL.md + supporting files)
    Outputs: .claude/skills/<skill-name>/ (same structure; .cursor/rules/
    references inside markdown files are rewritten to .claude/rules/).
    """
    claude_skills = out_dir / ".claude" / "skills"
    created: list[Path] = []

    if not cursor_skills_dir.exists():
        return created

    for skill_dir in sorted(p for p in cursor_skills_dir.iterdir() if p.is_dir()):
        dest_skill_dir = claude_skills / skill_dir.name
        for file_path in sorted(skill_dir.rglob("*")):
            if file_path.is_dir():
                continue
            rel = file_path.relative_to(skill_dir)
            out_path = dest_skill_dir / rel
            out_path.parent.mkdir(parents=True, exist_ok=True)
            if file_path.suffix == ".md":
                text = file_path.read_text(encoding="utf-8")
                text = _rule_body_to_claude(text)
                out_path.write_text(text, encoding="utf-8")
            else:
                shutil.copy2(file_path, out_path)
            created.append(out_path)

    return created


def convert_templates(cursor_templates_dir: Path, out_dir: Path) -> list[Path]:
    """Copy .cursor/templates/ to .claude/templates/, rewriting path references."""
    dest_dir = out_dir / ".claude" / "templates"
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
            text = _rule_body_to_claude(file_path.read_text(encoding="utf-8"))
            out_path.write_text(text, encoding="utf-8")
        else:
            shutil.copy2(file_path, out_path)
        created.append(out_path)
    return created


def write_settings(out_dir: Path) -> Path:
    """Write .claude/settings.json with permissions and AAMAD_TARGET_RUNTIME."""
    claude_dir = out_dir / ".claude"
    claude_dir.mkdir(parents=True, exist_ok=True)
    settings_path = claude_dir / "settings.json"

    settings = {
        "permissions": {
            "allow": [
                "Bash(python *)",
                "Bash(pip *)",
                "Bash(crewai *)",
                "Bash(npm *)",
                "Bash(npx *)",
                "Read(**)",
                "Edit(**)",
            ]
        },
        "env": {
            "AAMAD_TARGET_RUNTIME": "crewai",
        },
    }
    settings_path.write_text(json.dumps(settings, indent=2), encoding="utf-8")
    return settings_path


def install_claude_code(
    cursor_root: Path,
    dest: Path,
    *,
    overwrite: bool = False,
) -> list[Path]:
    """
    Run full Claude Code conversion: rules, agents, prompts, settings.

    Args:
        cursor_root: Project root containing .cursor/
        dest: Output directory (usually same as cursor_root)
        overwrite: If False, raise FileExistsError when target exists

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

    created: list[Path] = []

    claude_dir = dest / ".claude"
    if not overwrite and claude_dir.exists():
        # Quick preflight: if .claude exists and has content, we might overwrite
        existing = list(claude_dir.rglob("*"))
        if any(p.is_file() for p in existing):
            raise FileExistsError(
                f"{claude_dir} already exists and contains files. Use overwrite=True to replace."
            )

    created.extend(convert_rules(cursor_rules, dest, style="split"))
    if cursor_agents.exists():
        created.extend(convert_agents(cursor_agents, dest))
    if cursor_prompts.exists():
        created.extend(convert_prompts(cursor_prompts, dest))
    if cursor_skills.exists():
        created.extend(convert_skills(cursor_skills, dest))
    if cursor_templates.exists():
        created.extend(convert_templates(cursor_templates, dest))
    write_settings(dest)
    created.append(dest / ".claude" / "settings.json")

    return created
