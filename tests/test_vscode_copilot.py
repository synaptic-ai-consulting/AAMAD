"""Unit tests for VS Code / GitHub Copilot conversion logic."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from aamad.installer import extract_artifacts
from aamad.vscode_copilot import (
    convert_agents,
    convert_prompts,
    convert_rules,
    get_vscode_planned_paths,
    install_vscode_copilot,
    write_settings,
)


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
description: Core, framework-agnostic rules for AAMAD; applies to all personas.
alwaysApply: true
---

## Purpose
- Define universal principles and contracts.
"""
    (rules_dir / "aamad-core.mdc").write_text(content)
    return rules_dir


@pytest.fixture
def sample_mdc_with_globs(tmpdir):
    """Create a rule with globs (no alwaysApply)."""
    rules_dir = tmpdir / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    content = """---
description: Scoped rule for Python files
globs: ["src/**/*.py"]
---

## Scope
Only for Python source.
"""
    (rules_dir / "scoped.mdc").write_text(content)
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
def sample_agent_with_handoffs(tmpdir):
    """Create integration-eng agent (has handoffs to qa-eng)."""
    agents_dir = tmpdir / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    content = """---
agent:
  name: Integration Engineer
  id: integration-eng
  role: Integrates frontend with backend API for MVP.
---

# Persona: Integration Engineer

You wire up the MVP chat flow.
"""
    (agents_dir / "integration-eng.md").write_text(content)
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
    from aamad.vscode_copilot import _parse_frontmatter

    content = """---
description: Test
alwaysApply: true
---

## Purpose
- Define principles.
"""
    fm, body = _parse_frontmatter(content)
    assert fm.get("description") == "Test"
    assert "## Purpose" in body
    assert "Define principles" in body


def test_rule_apply_to_always_apply():
    """alwaysApply: true -> applyTo: '**'."""
    from aamad.vscode_copilot import _rule_apply_to

    assert _rule_apply_to({"alwaysApply": True}) == "**"
    assert _rule_apply_to({"alwaysApply": True, "globs": ["x"]}) == "**"


def test_rule_apply_to_globs():
    """globs list -> first element as applyTo."""
    from aamad.vscode_copilot import _rule_apply_to

    assert _rule_apply_to({"globs": ["src/**/*.py"]}) == "src/**/*.py"
    assert _rule_apply_to({"globs": ["a", "b"]}) == "a"


def test_rule_apply_to_empty_globs():
    """No globs or empty -> '**'."""
    from aamad.vscode_copilot import _rule_apply_to

    assert _rule_apply_to({}) == "**"
    assert _rule_apply_to({"globs": []}) == "**"
    assert _rule_apply_to({"globs": None}) == "**"


def test_convert_rules_creates_instructions(tmpdir, sample_mdc):
    """convert_rules creates .github/instructions/*.instructions.md with frontmatter and body."""
    out = convert_rules(sample_mdc, tmpdir)
    assert len(out) >= 1
    inst_file = tmpdir / ".github" / "instructions" / "aamad-core.instructions.md"
    assert inst_file.exists()
    text = inst_file.read_text()
    assert "---" in text
    assert "applyTo" in text
    assert "**" in text
    assert "name" in text
    assert "description" in text
    assert "## Purpose" in text
    assert "Define universal principles" in text


def test_convert_rules_globs_mapping(tmpdir):
    """Rule with globs gets applyTo from first glob."""
    rules_dir = tmpdir / "rules"
    rules_dir.mkdir()
    (rules_dir / "aamad-core.mdc").write_text(
        """---
description: Core rules
globs: ["src/**/*.py"]
---

## Body
"""
    )
    out = convert_rules(rules_dir, tmpdir)
    assert len(out) == 1
    text = out[0].read_text()
    assert "src/**/*.py" in text
    assert "## Body" in text


def test_convert_agents_creates_vscode_format(tmpdir, sample_agent):
    """convert_agents creates .github/agents/*.agent.md with name, description, tools."""
    out = convert_agents(sample_agent, tmpdir)
    assert len(out) == 1
    agent_file = tmpdir / ".github" / "agents" / "backend-eng.agent.md"
    assert agent_file.exists()
    text = agent_file.read_text()
    assert "---" in text
    assert "name:" in text
    assert "Backend Developer" in text
    assert "description:" in text
    assert "CrewAI backend" in text
    assert "tools:" in text
    assert "editFiles" in text
    assert "Persona: Backend Developer" in text


def test_convert_agents_handoffs(tmpdir, sample_agent_with_handoffs):
    """Agents with handoffs get handoffs in frontmatter."""
    out = convert_agents(sample_agent_with_handoffs, tmpdir)
    assert len(out) == 1
    agent_file = tmpdir / ".github" / "agents" / "integration-eng.agent.md"
    assert agent_file.exists()
    text = agent_file.read_text()
    assert "handoffs" in text
    assert "qa-eng" in text
    assert "Run QA" in text or "Run functional" in text


def test_convert_agents_restricts_fetch(tmpdir, sample_agent):
    """Build personas do not include 'fetch' in tools list."""
    out = convert_agents(sample_agent, tmpdir)
    assert len(out) == 1
    text = (tmpdir / ".github" / "agents" / "backend-eng.agent.md").read_text()
    # Frontmatter is between first and second ---; backend-eng must not have fetch in tools
    parts = text.split("---")
    assert len(parts) >= 2
    frontmatter_block = parts[1]
    assert "- fetch" not in frontmatter_block
    assert "editFiles" in frontmatter_block


def test_convert_prompts_creates_prompt_file(tmpdir, sample_prompt):
    """convert_prompts creates .github/prompts/phase-1-define.prompt.md with frontmatter."""
    out = convert_prompts(sample_prompt, tmpdir)
    assert len(out) == 1
    prompt_file = tmpdir / ".github" / "prompts" / "phase-1-define.prompt.md"
    assert prompt_file.exists()
    text = prompt_file.read_text()
    assert "---" in text
    assert "Phase 1" in text or "Market Research" in text
    assert "product-mgr" in text
    assert "Generate Market Research" in text or "PRD" in text


def test_convert_prompts_missing_returns_empty(tmpdir):
    """convert_prompts returns [] when prompt-phase-1 does not exist."""
    prompts_dir = tmpdir / "prompts"
    prompts_dir.mkdir()
    out = convert_prompts(prompts_dir, tmpdir)
    assert out == []


def test_write_settings_creates_valid_json(tmpdir):
    """write_settings creates valid .vscode/settings.json with expected keys."""
    path = write_settings(tmpdir, merge=False)
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["chat.agent.enabled"] is True
    assert data["chat.useAgentsMdFile"] is True
    assert ".github/instructions" in data["chat.instructionsFilesLocations"]
    assert ".github/agents" in data["chat.agentFilesLocations"]


def test_write_settings_merge_preserves_existing(tmpdir):
    """write_settings with merge=True preserves other keys in existing settings."""
    vscode_dir = tmpdir / ".vscode"
    vscode_dir.mkdir()
    existing = {"editor.tabSize": 4, "chat.agent.enabled": False}
    (vscode_dir / "settings.json").write_text(json.dumps(existing, indent=2))

    path = write_settings(tmpdir, merge=True)
    data = json.loads(path.read_text())
    assert data["editor.tabSize"] == 4
    assert data["chat.agent.enabled"] is True
    assert ".github/instructions" in data["chat.instructionsFilesLocations"]


def test_install_vscode_copilot_full(tmpdir):
    """install_vscode_copilot produces rules, agents, prompts, and settings."""
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
    created = install_vscode_copilot(cursor_root, dest, overwrite=False)

    assert len(created) >= 4
    assert (dest / ".github" / "instructions" / "aamad-core.instructions.md").exists()
    assert (dest / ".github" / "agents" / "backend-eng.agent.md").exists()
    assert (dest / ".github" / "prompts" / "phase-1-define.prompt.md").exists()
    assert (dest / ".vscode" / "settings.json").exists()


def test_install_vscode_copilot_overwrite_false_raises(tmpdir):
    """install_vscode_copilot raises FileExistsError when .github exists and overwrite=False."""
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
    (dest / ".github" / "instructions").mkdir(parents=True)
    (dest / ".github" / "instructions" / "aamad-core.instructions.md").write_text("existing")

    with pytest.raises(FileExistsError, match="already exists"):
        install_vscode_copilot(cursor_root, dest, overwrite=False)


def test_get_vscode_planned_paths():
    """get_vscode_planned_paths returns all paths that install would create."""
    from aamad.vscode_copilot import AGENT_IDS, RULE_ORDER

    dest = Path("/some/dest")
    paths = get_vscode_planned_paths(dest)
    assert len(paths) == len(RULE_ORDER) + len(AGENT_IDS) + 2  # + prompts file + settings
    assert dest / ".vscode" / "settings.json" in paths
    assert dest / ".github" / "prompts" / "phase-1-define.prompt.md" in paths


def test_extract_artifacts_vscode_creates_github_and_agents_md(tmpdir):
    """extract_artifacts with ide=vscode creates .github/, .vscode/, and AGENTS.md with vscode note."""
    paths = extract_artifacts(tmpdir, ide="vscode", overwrite=False)
    assert (tmpdir / ".github" / "instructions").exists()
    assert (tmpdir / ".github" / "agents").exists()
    assert (tmpdir / ".vscode" / "settings.json").exists()
    assert (tmpdir / "AGENTS.md").exists()
    agents_md = (tmpdir / "AGENTS.md").read_text()
    assert ".github/agents/" in agents_md
    assert "VS Code" in agents_md or "Copilot" in agents_md
