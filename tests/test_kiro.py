"""Unit tests for Kiro conversion logic."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
import yaml

from aamad.installer import extract_artifacts, write_agents_md
from aamad.kiro import (
    AGENT_IDS,
    RULE_ORDER,
    TEMPLATE_FILES,
    convert_agents,
    convert_dev_crew_steering,
    convert_prompts,
    convert_rules,
    convert_skills,
    convert_templates,
    get_kiro_planned_paths,
    install_kiro,
)


@pytest.fixture
def tmpdir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture
def sample_mdc(tmpdir):
    rules_dir = tmpdir / "rules"
    rules_dir.mkdir()
    (rules_dir / "aamad-core.mdc").write_text(
        """---
description: Core, framework-agnostic rules for AAMAD; applies to all personas.
alwaysApply: true
---

## Purpose
- See `.cursor/rules/epics-index.mdc` for mapping.
"""
    )
    return rules_dir


@pytest.fixture
def sample_agent(tmpdir):
    agents_dir = tmpdir / "agents"
    agents_dir.mkdir()
    (agents_dir / "backend-eng.md").write_text(
        """---
agent:
  name: Backend Developer
  id: backend-eng
  role: Implements the MVP backend.
instructions:
  - Only build the backend as specified in SAD.
---

# Persona: Backend Developer (@backend.eng)

You own the backend for MVP.
"""
    )
    (agents_dir / "product-mgr.md").write_text(
        """---
agent:
  name: Product Manager
  id: product-mgr
  role: Context and requirements synthesis.
---

# Persona: Product Manager (@product-mgr)
"""
    )
    (agents_dir / "qa-eng.md").write_text(
        """---
agent:
  name: QA Engineer
  id: qa-eng
  role: Validate that the MVP works as intended.
---

# Persona: QA Engineer (@qa.eng)
"""
    )
    return agents_dir


@pytest.fixture
def sample_prompt(tmpdir):
    prompts_dir = tmpdir / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "prompt-phase-1").write_text(
        "Generate Market Research and PRD using the templates."
    )
    (prompts_dir / "prompt-sync-docs").write_text("Synchronize project-context docs.")
    return prompts_dir


@pytest.fixture
def sample_skill(tmpdir):
    skills_dir = tmpdir / "skills"
    skill_dir = skills_dir / "run-evals"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        """---
name: run-evals
description: Test eval skill.
---

# Run Evals

See `.cursor/rules/epics-index.mdc` for the Evals epic.
"""
    )
    (skill_dir / "reference.md").write_text("Calibration notes.")
    return skills_dir


def test_convert_rules_writes_always_inclusion_and_rewrites_paths(sample_mdc, tmpdir):
    dest = tmpdir / "out"
    created = convert_rules(sample_mdc, dest)
    out = dest / ".kiro" / "steering" / "aamad-core.md"
    assert out in created
    text = out.read_text()
    fm, body = text.split("---\n", 2)[1], text.split("---\n", 2)[2]
    data = yaml.safe_load(fm)
    assert data["inclusion"] == "always"
    assert ".kiro/steering/epics-index.md" in body
    assert ".cursor/rules/" not in body


def test_convert_dev_crew_steering(tmpdir):
    agents_dir = tmpdir / "agents"
    agents_dir.mkdir()
    (agents_dir / "dev-crew.md").write_text("# AAMAD Development Crew\n")
    dest = tmpdir / "out"
    created = convert_dev_crew_steering(agents_dir, dest)
    out = dest / ".kiro" / "steering" / "dev-crew.md"
    assert created == [out]
    assert "inclusion: always" in out.read_text()
    assert "AAMAD Development Crew" in out.read_text()


def test_convert_agents_tools_and_resources(sample_agent, tmpdir):
    dest = tmpdir / "out"
    created = convert_agents(sample_agent, dest)
    by_name = {p.name: p for p in created}

    backend = yaml.safe_load(by_name["backend-eng.md"].read_text().split("---")[1])
    assert backend["name"] == "Backend Developer"
    assert backend["tools"] == ["read", "write", "shell"]
    assert backend["resources"] == ["file://.kiro/steering/**/*.md"]

    product = yaml.safe_load(by_name["product-mgr.md"].read_text().split("---")[1])
    assert "web" in product["tools"]
    assert product["resources"] == ["file://.kiro/steering/**/*.md"]

    qa = yaml.safe_load(by_name["qa-eng.md"].read_text().split("---")[1])
    assert qa["tools"] == ["read", "write", "shell"]
    assert "skill://.kiro/skills/**/SKILL.md" in qa["resources"]


def test_convert_prompts_are_manual_steering(sample_prompt, tmpdir):
    dest = tmpdir / "out"
    created = convert_prompts(sample_prompt, dest)
    names = {p.name for p in created}
    assert names == {"phase-1-define.md", "sync-docs.md"}
    for path in created:
        fm = yaml.safe_load(path.read_text().split("---")[1])
        assert fm["inclusion"] == "manual"
    assert "Market Research" in (dest / ".kiro" / "steering" / "phase-1-define.md").read_text()


def test_convert_skills_copies_and_rewrites_paths(sample_skill, tmpdir):
    dest = tmpdir / "out"
    created = convert_skills(sample_skill, dest)
    skill_md = dest / ".kiro" / "skills" / "run-evals" / "SKILL.md"
    reference = dest / ".kiro" / "skills" / "run-evals" / "reference.md"
    assert skill_md in created
    assert reference in created
    text = skill_md.read_text()
    assert ".kiro/steering/epics-index.md" in text
    assert ".cursor/rules/" not in text
    assert "Calibration notes." in reference.read_text()


def test_install_kiro_converts_full_tree(tmpdir):
    cursor_root = tmpdir / "cursor"
    rules = cursor_root / ".cursor" / "rules"
    agents = cursor_root / ".cursor" / "agents"
    prompts = cursor_root / ".cursor" / "prompts"
    skills = cursor_root / ".cursor" / "skills" / "run-evals"
    rules.mkdir(parents=True)
    agents.mkdir(parents=True)
    prompts.mkdir(parents=True)
    skills.mkdir(parents=True)
    (rules / "aamad-core.mdc").write_text(
        "---\nalwaysApply: true\n---\n\n## Purpose\nCore.\n"
    )
    (agents / "backend-eng.md").write_text(
        "---\nagent:\n  name: Backend Developer\n  id: backend-eng\n  role: Backend.\n---\n\nBody.\n"
    )
    (agents / "dev-crew.md").write_text("# Crew\n")
    (prompts / "prompt-phase-1").write_text("Phase 1")
    (skills / "SKILL.md").write_text("---\nname: run-evals\n---\n\nEval.\n")

    dest = tmpdir / "out"
    created = install_kiro(cursor_root, dest, overwrite=False)
    assert dest / ".kiro" / "steering" / "aamad-core.md" in created
    assert dest / ".kiro" / "steering" / "dev-crew.md" in created
    assert dest / ".kiro" / "steering" / "phase-1-define.md" in created
    assert dest / ".kiro" / "agents" / "backend-eng.md" in created
    assert dest / ".kiro" / "skills" / "run-evals" / "SKILL.md" in created
    assert not (dest / ".cursor").exists()


def test_install_kiro_overwrite_false_raises(tmpdir):
    cursor_root = tmpdir / "cursor"
    (cursor_root / ".cursor" / "rules").mkdir(parents=True)
    (cursor_root / ".cursor" / "rules" / "aamad-core.mdc").write_text(
        "---\nalwaysApply: true\n---\n\n## Purpose\nCore.\n"
    )
    dest = tmpdir / "out"
    (dest / ".kiro" / "steering").mkdir(parents=True)
    (dest / ".kiro" / "steering" / "aamad-core.md").write_text("existing")
    with pytest.raises(FileExistsError, match="already exists"):
        install_kiro(cursor_root, dest, overwrite=False)


def test_get_kiro_planned_paths():
    dest = Path("/some/dest")
    paths = get_kiro_planned_paths(dest)
    assert dest / ".kiro" / "steering" / "aamad-core.md" in paths
    assert dest / ".kiro" / "steering" / "dev-crew.md" in paths
    assert dest / ".kiro" / "steering" / "phase-1-define.md" in paths
    assert dest / ".kiro" / "agents" / "backend-eng.md" in paths
    assert dest / ".kiro" / "templates" / "prd-template.md" in paths
    assert len(paths) == len(RULE_ORDER) + 1 + 2 + len(AGENT_IDS) + len(TEMPLATE_FILES)


def test_write_agents_md_kiro(tmpdir):
    path = write_agents_md(tmpdir, ide="kiro", overwrite=True)
    assert path is not None
    text = path.read_text()
    assert ".kiro/agents/" in text


def test_extract_artifacts_kiro_layout(tmpdir):
    paths = extract_artifacts(tmpdir, ide="kiro", overwrite=False)
    assert (tmpdir / ".kiro" / "steering" / "aamad-core.md").exists()
    assert (tmpdir / ".kiro" / "steering" / "dev-crew.md").exists()
    assert (tmpdir / ".kiro" / "steering" / "phase-1-define.md").exists()
    assert (tmpdir / ".kiro" / "steering" / "sync-docs.md").exists()
    for agent_id in AGENT_IDS:
        assert (tmpdir / ".kiro" / "agents" / f"{agent_id}.md").exists()
    assert (tmpdir / ".kiro" / "skills" / "run-evals" / "SKILL.md").exists()
    assert (tmpdir / ".kiro" / "templates" / "prd-template.md").exists()
    assert not (tmpdir / ".cursor").exists()
    assert (tmpdir / "project-context").exists()
    assert (tmpdir / "AGENTS.md").exists()
    agents_md = (tmpdir / "AGENTS.md").read_text()
    assert ".kiro/agents/" in agents_md
    assert any(p.name == "AGENTS.md" for p in paths)

    backend = yaml.safe_load(
        (tmpdir / ".kiro" / "agents" / "backend-eng.md").read_text().split("---")[1]
    )
    product = yaml.safe_load(
        (tmpdir / ".kiro" / "agents" / "product-mgr.md").read_text().split("---")[1]
    )
    qa = yaml.safe_load(
        (tmpdir / ".kiro" / "agents" / "qa-eng.md").read_text().split("---")[1]
    )
    assert backend["tools"] == ["read", "write", "shell"]
    assert "web" in product["tools"]
    assert "skill://.kiro/skills/**/SKILL.md" in qa["resources"]
    product_body = (tmpdir / ".kiro" / "agents" / "product-mgr.md").read_text()
    assert ".kiro/templates/" in product_body
    assert ".cursor/templates/" not in product_body
    prompt = (tmpdir / ".kiro" / "steering" / "phase-1-define.md").read_text()
    assert ".kiro/templates/" in prompt
    assert ".cursor/templates/" not in prompt


def test_convert_templates_rewrites_paths(tmpdir):
    templates = tmpdir / "templates"
    templates.mkdir()
    (templates / "prd-template.md").write_text(
        "See `.cursor/templates/mrd-template.md` and `.cursor/rules/aamad-core.mdc`.\n"
    )
    dest = tmpdir / "out"
    created = convert_templates(templates, dest)
    out = dest / ".kiro" / "templates" / "prd-template.md"
    assert out in created
    text = out.read_text()
    assert ".kiro/templates/mrd-template.md" in text
    assert ".kiro/steering/aamad-core.md" in text
    assert ".cursor/" not in text


def test_extract_artifacts_kiro_dry_run_writes_nothing(tmpdir):
    paths = extract_artifacts(tmpdir, ide="kiro", overwrite=False, dry_run=True)
    assert paths
    assert not (tmpdir / ".kiro").exists()
    assert not (tmpdir / "AGENTS.md").exists()
    assert any(p.name == "aamad-core.md" for p in paths)
    assert any(str(p).endswith(".kiro/skills/run-evals/SKILL.md") for p in paths)
    assert any(str(p).endswith(".kiro/templates/prd-template.md") for p in paths)
