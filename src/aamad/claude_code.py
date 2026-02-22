"""
Claude Code IDE conversion logic for AAMAD.

Converts Cursor-format artifacts (.cursor/rules/*.mdc, .cursor/agents/*.md,
.cursor/prompts/) into Claude Code format (.claude/rules/, .claude/agents/,
.claude/commands/, .claude/settings.json).
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

# Rule order for CLAUDE.md summary and split output (dependency order)
RULE_ORDER = [
    "aamad-core",
    "development-workflow",
    "epics-index",
    "adapter-registry",
    "adapter-crewai",
]

# Agent files to convert (exclude personas.md index)
AGENT_IDS = [
    "product-mgr",
    "system-arch",
    "project-mgr",
    "frontend-eng",
    "backend-eng",
    "integration-eng",
    "qa-eng",
]

# Default tools for Claude Code agents (most personas need these)
DEFAULT_TOOLS = "Read, Edit, Write, Bash, Grep, Glob"

# Agents that should not use WebFetch (build personas)
DISALLOW_WEBFETCH_IDS = {"backend-eng", "frontend-eng", "integration-eng", "qa-eng", "project-mgr"}


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
    """Update path references from .cursor/rules/ to .claude/rules/ for Claude Code."""
    # Update .cursor/rules/foo.mdc -> .claude/rules/foo.md
    body = re.sub(
        r"\.cursor/rules/([^\s\)\"']+\.)mdc",
        r".claude/rules/\1md",
        body,
    )
    # Catch any remaining .cursor/rules/ (without .mdc)
    body = body.replace(".cursor/rules/", ".claude/rules/")
    return body


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

    Skips personas.md (index file). Converts only files matching AGENT_IDS.
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

        # Ensure body has proper heading; keep original body
        new_content = "\n".join(frontmatter_lines) + body
        out_path = claude_agents / f"{agent_id}.md"
        out_path.write_text(new_content, encoding="utf-8")
        created.append(out_path)

    return created


def convert_prompts(
    cursor_prompts_dir: Path,
    out_dir: Path,
) -> list[Path]:
    """
    Convert Phase 1 prompt to Claude Code command.

    Input: .cursor/prompts/prompt-phase-1 (no extension)
    Output: .claude/commands/phase-1-define.md
    """
    claude_commands = out_dir / ".claude" / "commands"
    claude_commands.mkdir(parents=True, exist_ok=True)

    prompt_path = cursor_prompts_dir / "prompt-phase-1"
    if not prompt_path.exists():
        return []

    content = prompt_path.read_text(encoding="utf-8")
    out_path = claude_commands / "phase-1-define.md"
    out_path.write_text(content, encoding="utf-8")
    return [out_path]


def write_settings(out_dir: Path) -> Path:
    """Write .claude/settings.json with permissions and AAMAD_ADAPTER."""
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
            "AAMAD_ADAPTER": "crewai",
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
    write_settings(dest)
    created.append(dest / ".claude" / "settings.json")

    return created
