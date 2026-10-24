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
    convert_skills,
    convert_templates,
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
  - project-context/1.define/prd.md
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


@pytest.fixture
def sample_skill(tmpdir):
    """Create a sample Cursor skill with a SKILL.md and a reference file."""
    skills_dir = tmpdir / "skills"
    skill_dir = skills_dir / "run-evals"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        """---
name: run-evals
description: Test eval skill.
disable-model-invocation: true
---

# Run Evals

See .cursor/rules/adapter-crewai.mdc for details.
"""
    )
    (skill_dir / "reference.md").write_text("# Reference\n\nExtra detail.\n")
    return skills_dir


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


def test_convert_prompts_creates_sync_docs(tmpdir):
    """convert_prompts creates .claude/commands/sync-docs.md when source exists."""
    prompts_dir = tmpdir / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "prompt-sync-docs").write_text("Synchronize project-context docs.")
    out = convert_prompts(prompts_dir, tmpdir)
    assert any(p.name == "sync-docs.md" for p in out)
    assert (tmpdir / ".claude" / "commands" / "sync-docs.md").exists()


def test_convert_skills_creates_skill_dir(tmpdir, sample_skill):
    """convert_skills creates .claude/skills/run-evals/SKILL.md and reference.md."""
    out = convert_skills(sample_skill, tmpdir)
    assert len(out) == 2
    skill_md = tmpdir / ".claude" / "skills" / "run-evals" / "SKILL.md"
    reference_md = tmpdir / ".claude" / "skills" / "run-evals" / "reference.md"
    assert skill_md.exists()
    assert reference_md.exists()
    assert "Run Evals" in skill_md.read_text()
    assert "Extra detail." in reference_md.read_text()


def test_convert_skills_rewrites_rule_paths(tmpdir, sample_skill):
    """convert_skills rewrites .cursor/rules/*.mdc references to .claude/rules/*.md."""
    convert_skills(sample_skill, tmpdir)
    skill_md = tmpdir / ".claude" / "skills" / "run-evals" / "SKILL.md"
    text = skill_md.read_text()
    assert ".claude/rules/adapter-crewai.md" in text
    assert ".cursor/rules/" not in text


def test_convert_skills_missing_dir_returns_empty(tmpdir):
    """convert_skills returns [] when the skills directory does not exist."""
    out = convert_skills(tmpdir / "nonexistent", tmpdir)
    assert out == []


def test_write_settings_creates_valid_json(tmpdir):
    """write_settings creates valid .claude/settings.json."""
    path = write_settings(tmpdir)
    assert path.exists()
    data = json.loads(path.read_text())
    assert "permissions" in data
    assert "allow" in data["permissions"]
    assert "env" in data
    assert data["env"]["AAMAD_TARGET_RUNTIME"] == "crewai"


def test_convert_rules_includes_all_runtime_adapter_rules(tmpdir):
    """convert_rules writes all runtime adapter rule files when present."""
    rules_dir = tmpdir / "rules"
    rules_dir.mkdir()
    (rules_dir / "aamad-core.mdc").write_text(
        """---
description: Core rules
alwaysApply: true
---

## Purpose
Core.
"""
    )
    (rules_dir / "adapter-registry.mdc").write_text(
        """---
description: Registry
alwaysApply: true
---

## Purpose
Registry.
"""
    )
    (rules_dir / "adapter-crewai.mdc").write_text(
        """---
description: CrewAI adapter
alwaysApply: true
---

## Purpose
CrewAI.
"""
    )
    (rules_dir / "adapter-claude-agent-sdk.mdc").write_text(
        """---
description: Claude Agent SDK adapter
alwaysApply: true
---

## Purpose
Claude.
"""
    )
    (rules_dir / "adapter-cursor-sdk.mdc").write_text(
        """---
description: Cursor SDK adapter
alwaysApply: true
---

## Purpose
Cursor.
"""
    )

    convert_rules(rules_dir, tmpdir, style="split")
    out_dir = tmpdir / ".claude" / "rules"
    assert (out_dir / "adapter-crewai.md").exists()
    assert (out_dir / "adapter-claude-agent-sdk.md").exists()
    assert (out_dir / "adapter-cursor-sdk.md").exists()


def test_convert_rules_includes_delivery_workflow(tmpdir):
    """convert_rules writes delivery-workflow when present."""
    rules_dir = tmpdir / "rules"
    rules_dir.mkdir()
    (rules_dir / "delivery-workflow.mdc").write_text(
        """---
description: Deliver workflow
alwaysApply: true
---

## Purpose
Deliver.
"""
    )
    convert_rules(rules_dir, tmpdir, style="split")
    assert (tmpdir / ".claude" / "rules" / "delivery-workflow.md").exists()


def test_convert_agents_includes_devops_eng(tmpdir):
    """convert_agents writes devops-eng when source file exists."""
    agents_dir = tmpdir / "agents"
    agents_dir.mkdir()
    (agents_dir / "devops-eng.md").write_text(
        """---
agent:
  name: DevOps Engineer
  id: devops-eng
  role: Operationalize MVP delivery.
---

# DevOps
"""
    )
    out = convert_agents(agents_dir, tmpdir)
    assert len(out) == 1
    assert (tmpdir / ".claude" / "agents" / "devops-eng.md").exists()


def test_convert_agents_includes_security_eng(tmpdir):
    """convert_agents writes security-eng when source file exists."""
    agents_dir = tmpdir / "agents"
    agents_dir.mkdir()
    (agents_dir / "security-eng.md").write_text(
        """---
agent:
  name: Security Engineer
  id: security-eng
  role: Assess MVP security.
---

# Security
"""
    )
    out = convert_agents(agents_dir, tmpdir)
    assert len(out) == 1
    assert (tmpdir / ".claude" / "agents" / "security-eng.md").exists()


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
    (cursor_root / ".cursor" / "skills" / "run-evals").mkdir(parents=True)
    (cursor_root / ".cursor" / "skills" / "run-evals" / "SKILL.md").write_text(
        "---\nname: run-evals\ndescription: Test.\n---\n\n# Run Evals\n"
    )

    dest = tmpdir / "out"
    dest.mkdir()
    created = install_claude_code(cursor_root, dest, overwrite=False)

    assert len(created) >= 5
    assert (dest / ".claude" / "CLAUDE.md").exists()
    assert (dest / ".claude" / "rules" / "aamad-core.md").exists()
    assert (dest / ".claude" / "agents" / "backend-eng.md").exists()
    assert (dest / ".claude" / "commands" / "phase-1-define.md").exists()
    assert (dest / ".claude" / "skills" / "run-evals" / "SKILL.md").exists()
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
    assert (tmpdir / ".cursor" / "templates" / "prd-template.md").exists()
    product = (tmpdir / ".cursor" / "agents" / "product-mgr.md").read_text()
    assert ".cursor/templates/" in product


def test_convert_templates_rewrites_paths(tmpdir):
    templates = tmpdir / "templates"
    templates.mkdir()
    (templates / "prd-template.md").write_text(
        "See `.cursor/templates/mrd-template.md` and `.cursor/rules/aamad-core.mdc`.\n"
    )
    dest = tmpdir / "out"
    created = convert_templates(templates, dest)
    out = dest / ".claude" / "templates" / "prd-template.md"
    assert out in created
    text = out.read_text()
    assert ".claude/templates/mrd-template.md" in text
    assert ".claude/rules/aamad-core.md" in text
    assert ".cursor/" not in text


def test_extract_artifacts_claude_code_has_templates_and_no_cursor(tmpdir):
    extract_artifacts(tmpdir, ide="claude-code", overwrite=False)
    assert (tmpdir / ".claude" / "templates" / "prd-template.md").exists()
    assert (tmpdir / ".claude" / "agents" / "product-mgr.md").exists()
    assert not (tmpdir / ".cursor").exists()
    product = (tmpdir / ".claude" / "agents" / "product-mgr.md").read_text()
    assert ".claude/templates/" in product
    assert ".cursor/templates/" not in product
    prompt = (tmpdir / ".claude" / "commands" / "phase-1-define.md").read_text()
    assert ".claude/templates/" in prompt
    assert ".cursor/templates/" not in prompt
