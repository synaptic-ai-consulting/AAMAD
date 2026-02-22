"""Unit tests for Claude Code conversion logic."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from aamad.claude_code import (
    convert_agents,
    convert_prompts,
    convert_rules,
    install_claude_code,
    write_settings,
)
from aamad.installer import extract_artifacts, write_agents_md


@pytest.fixture
def tmpdir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture
def sample_mdc(tmpdir):
    """Create a sample .mdc rule file."""
    rules_dir = tmpdir / "rules"
    rules_dir.mkdir()
    content = """---
description: Test rule for AAMAD
alwaysApply: true
---

## Purpose
- Define test principles.

## Reference
See .cursor/rules/epics-index.mdc for more.
"""
    (rules_dir / "aamad-core.mdc").write_text(content)
    return rules_dir


@pytest.fixture
def sample_agent(tmpdir):
    """Create a sample Cursor agent file."""
    agents_dir = tmpdir / "agents"
    agents_dir.mkdir()
    content = """---
agent:
  name: Backend Developer
  id: backend-eng
  role: Implements the MVP CrewAI backend.
instructions:
  - Only build CrewAI backend as specified in SAD.
  - Output to project-context/2.build/backend.md.
actions:
  - develop-be
  - define-agents
inputs:
  - project-context/product-requirements-document.md
outputs:
  - project-context/2.build/backend.md
prohibited-actions:
  - Implement persistent storage
---

# Persona: Backend Developer (@backend.eng)

You own the CrewAI backend and agent scaffolding for MVP.
"""
    (agents_dir / "backend-eng.md").write_text(content)
    return agents_dir


@pytest.fixture
def sample_prompt(tmpdir):
    """Create a sample Phase 1 prompt."""
    prompts_dir = tmpdir / "prompts"
    prompts_dir.mkdir()
    content = "Generate Market Research and PRD using the templates."
    (prompts_dir / "prompt-phase-1").write_text(content)
    return prompts_dir


def test_parse_frontmatter_rule_extracts_body():
    """Rule body is preserved after stripping frontmatter."""
    from aamad.claude_code import _parse_frontmatter

    content = """---
description: Test
alwaysApply: true
---

## Purpose
- Define principles.
"""
    fm, body = _parse_frontmatter(content)
    assert "description" in fm or "alwaysApply" in fm
    assert "## Purpose" in body
    assert "Define principles" in body


def test_convert_rules_split_creates_files(tmpdir, sample_mdc):
    """convert_rules creates CLAUDE.md and rules/*.md in split style."""
    out = convert_rules(sample_mdc, tmpdir, style="split")
    assert len(out) >= 2
    claude_md = tmpdir / ".claude" / "CLAUDE.md"
    assert claude_md.exists()
    text = claude_md.read_text()
    assert "AAMAD" in text
    assert ".claude/rules/" in text

    rules_dir = tmpdir / ".claude" / "rules"
    assert rules_dir.exists()
    rule_file = rules_dir / "aamad-core.md"
    assert rule_file.exists()
    assert "Define test principles" in rule_file.read_text()


def test_convert_rules_path_replacement(tmpdir):
    """Path references .cursor/rules/ are replaced with .claude/rules/."""
    rules_dir = tmpdir / "rules"
    rules_dir.mkdir()
    (rules_dir / "aamad-core.mdc").write_text(
        """---
description: Core rules
alwaysApply: true
---

## Purpose
See .cursor/rules/epics-index.mdc for mapping.
"""
    )
    out = convert_rules(rules_dir, tmpdir, style="split")
    rule_file = tmpdir / ".claude" / "rules" / "aamad-core.md"
    assert rule_file.exists()
    body = rule_file.read_text()
    assert ".claude/rules/epics-index.md" in body or ".claude/rules/" in body
    assert ".cursor/rules/" not in body


def test_convert_agents_creates_claude_format(tmpdir, sample_agent):
    """convert_agents creates .claude/agents/*.md with Claude frontmatter."""
    out = convert_agents(sample_agent, tmpdir)
    assert len(out) == 1
    agent_file = tmpdir / ".claude" / "agents" / "backend-eng.md"
    assert agent_file.exists()
    text = agent_file.read_text()
    assert "---" in text
    assert "name: backend-eng" in text
    assert "description:" in text
    assert "tools:" in text
    assert "model: inherit" in text
    assert "Persona: Backend Developer" in text
    assert "CrewAI backend" in text


def test_convert_prompts_creates_command(tmpdir, sample_prompt):
    """convert_prompts creates .claude/commands/phase-1-define.md."""
    out = convert_prompts(sample_prompt, tmpdir)
    assert len(out) == 1
    cmd_file = tmpdir / ".claude" / "commands" / "phase-1-define.md"
    assert cmd_file.exists()
    assert "Market Research" in cmd_file.read_text()


def test_write_settings_creates_valid_json(tmpdir):
    """write_settings creates valid .claude/settings.json."""
    path = write_settings(tmpdir)
    assert path.exists()
    data = json.loads(path.read_text())
    assert "permissions" in data
    assert "allow" in data["permissions"]
    assert "env" in data
    assert data["env"]["AAMAD_ADAPTER"] == "crewai"


def test_install_claude_code_full(tmpdir):
    """install_claude_code produces all expected artifacts."""
    # Create minimal cursor structure
    cursor_root = tmpdir / "cursor"
    cursor_root.mkdir()
    (cursor_root / ".cursor" / "rules").mkdir(parents=True)
    (cursor_root / ".cursor" / "rules" / "aamad-core.mdc").write_text(
        """---
description: Core
alwaysApply: true
---

## Purpose
Core rules.
"""
    )
    (cursor_root / ".cursor" / "agents").mkdir(parents=True)
    (cursor_root / ".cursor" / "agents" / "backend-eng.md").write_text(
        """---
agent:
  name: Backend Developer
  id: backend-eng
  role: Implements backend.
---

# Backend
"""
    )
    (cursor_root / ".cursor" / "prompts").mkdir(parents=True)
    (cursor_root / ".cursor" / "prompts" / "prompt-phase-1").write_text("Phase 1 prompt.")

    dest = tmpdir / "out"
    dest.mkdir()
    created = install_claude_code(cursor_root, dest, overwrite=False)

    assert len(created) >= 5
    assert (dest / ".claude" / "CLAUDE.md").exists()
    assert (dest / ".claude" / "rules" / "aamad-core.md").exists()
    assert (dest / ".claude" / "agents" / "backend-eng.md").exists()
    assert (dest / ".claude" / "commands" / "phase-1-define.md").exists()
    assert (dest / ".claude" / "settings.json").exists()


def test_install_claude_code_overwrite_false_raises(tmpdir):
    """install_claude_code raises FileExistsError when target exists and overwrite=False."""
    cursor_root = tmpdir / "cursor"
    cursor_root.mkdir()
    (cursor_root / ".cursor" / "rules").mkdir(parents=True)
    (cursor_root / ".cursor" / "rules" / "aamad-core.mdc").write_text(
        """---
description: Core
alwaysApply: true
---

## Purpose
Core.
"""
    )
    dest = tmpdir / "out"
    dest.mkdir()
    (dest / ".claude" / "rules").mkdir(parents=True)
    (dest / ".claude" / "rules" / "aamad-core.md").write_text("existing")

    with pytest.raises(FileExistsError, match="already exists"):
        install_claude_code(cursor_root, dest, overwrite=False)


def test_write_agents_md_creates_bridge_file(tmpdir):
    """write_agents_md creates AGENTS.md with IDE-specific pointer."""
    path = write_agents_md(tmpdir, ide="claude-code", overwrite=False)
    assert path.exists()
    text = path.read_text()
    assert "AAMAD Agent Framework" in text
    assert ".claude/agents/" in text

    path2 = write_agents_md(tmpdir, ide="cursor", overwrite=True)
    assert path2.exists()
    text2 = path2.read_text()
    assert ".cursor/agents/" in text2


def test_extract_artifacts_includes_agents_md(tmpdir):
    """extract_artifacts creates AGENTS.md for both IDEs."""
    # Need real bundle - we'll use cursor since we have it
    paths = extract_artifacts(tmpdir, ide="cursor", overwrite=False)
    agents_md = tmpdir / "AGENTS.md"
    assert agents_md.exists()
    assert agents_md in paths or any(str(p).endswith("AGENTS.md") for p in paths)
    assert ".cursor/agents/" in agents_md.read_text()
