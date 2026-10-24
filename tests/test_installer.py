"""Installer tests for project mode and brownfield layout."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from aamad.installer import extract_artifacts, write_mode_artifacts


def test_greenfield_writes_mode_and_skips_review_dir(tmp_path: Path):
    extract_artifacts(tmp_path, ide="cursor", mode="greenfield")
    data = yaml.safe_load((tmp_path / "aamad.config.yml").read_text(encoding="utf-8"))
    assert data["project"]["mode"] == "greenfield"
    assert not (tmp_path / "project-context" / "0.review").exists()
    assert "Brownfield" in (tmp_path / "AGENTS.md").read_text(encoding="utf-8")


def test_brownfield_creates_review_dir(tmp_path: Path):
    extract_artifacts(tmp_path, ide="cursor", mode="brownfield")
    data = yaml.safe_load((tmp_path / "aamad.config.yml").read_text(encoding="utf-8"))
    assert data["project"]["mode"] == "brownfield"
    assert (tmp_path / "project-context" / "0.review" / ".gitkeep").is_file()


def test_brownfield_preserves_existing_readme(tmp_path: Path):
    (tmp_path / "README.md").write_text("existing project\n", encoding="utf-8")
    extract_artifacts(tmp_path, ide="cursor", mode="brownfield")
    assert (tmp_path / "README.md").read_text(encoding="utf-8") == "existing project\n"


def test_greenfield_existing_readme_raises(tmp_path: Path):
    (tmp_path / "README.md").write_text("mine\n", encoding="utf-8")
    with pytest.raises(FileExistsError):
        extract_artifacts(tmp_path, ide="cursor", mode="greenfield")


def test_merge_existing_config_keeps_other_keys(tmp_path: Path):
    (tmp_path / "aamad.config.yml").write_text(
        "version: 1\nlanguage:\n  primary: typescript\n",
        encoding="utf-8",
    )
    extract_artifacts(tmp_path, ide="cursor", mode="brownfield")
    data = yaml.safe_load((tmp_path / "aamad.config.yml").read_text(encoding="utf-8"))
    assert data["language"]["primary"] == "typescript"
    assert data["project"]["mode"] == "brownfield"


def test_brownfield_dry_run_lists_review_and_config(tmp_path: Path):
    paths = extract_artifacts(tmp_path, ide="cursor", mode="brownfield", dry_run=True)
    rendered = {str(p) for p in paths}
    assert any(p.endswith("aamad.config.yml") for p in rendered)
    assert any("0.review" in p and p.endswith(".gitkeep") for p in rendered)
    assert not (tmp_path / "aamad.config.yml").exists()
    assert not (tmp_path / "project-context" / "0.review").exists()


@pytest.mark.parametrize("ide", ["claude-code", "vscode", "kiro"])
def test_brownfield_non_cursor_preserves_readme_and_has_no_cursor(tmp_path: Path, ide: str):
    (tmp_path / "README.md").write_text("keep me\n", encoding="utf-8")
    extract_artifacts(tmp_path, ide=ide, mode="brownfield")
    assert (tmp_path / "README.md").read_text(encoding="utf-8") == "keep me\n"
    assert not (tmp_path / ".cursor").exists()
    assert (tmp_path / "project-context" / "0.review" / ".gitkeep").is_file()


def test_greenfield_runtime_writes_env_and_config(tmp_path: Path):
    extract_artifacts(tmp_path, ide="cursor", mode="greenfield", runtime="cursor-sdk")
    data = yaml.safe_load((tmp_path / "aamad.config.yml").read_text(encoding="utf-8"))
    assert data["runtime"]["target"] == "cursor-sdk"
    env = (tmp_path / ".env").read_text(encoding="utf-8")
    assert "AAMAD_TARGET_RUNTIME=cursor-sdk" in env


def test_greenfield_later_does_not_set_runtime(tmp_path: Path):
    extract_artifacts(tmp_path, ide="cursor", mode="greenfield", runtime="later")
    data = yaml.safe_load((tmp_path / "aamad.config.yml").read_text(encoding="utf-8"))
    assert "runtime" not in data
    assert not (tmp_path / ".env").exists()


def test_greenfield_omitted_runtime_does_not_set_variable(tmp_path: Path):
    extract_artifacts(tmp_path, ide="cursor", mode="greenfield")
    data = yaml.safe_load((tmp_path / "aamad.config.yml").read_text(encoding="utf-8"))
    assert "runtime" not in data
    assert not (tmp_path / ".env").exists()


def test_merge_dotenv_replaces_existing_runtime_key(tmp_path: Path):
    (tmp_path / ".env").write_text("FOO=keep\nAAMAD_TARGET_RUNTIME=crewai\n", encoding="utf-8")
    write_mode_artifacts(tmp_path, mode="greenfield", runtime="claude-agent-sdk")
    env = (tmp_path / ".env").read_text(encoding="utf-8")
    assert "FOO=keep" in env
    assert "AAMAD_TARGET_RUNTIME=claude-agent-sdk" in env
    assert "AAMAD_TARGET_RUNTIME=crewai" not in env


def test_claude_code_runtime_updates_settings(tmp_path: Path):
    extract_artifacts(
        tmp_path, ide="claude-code", mode="greenfield", runtime="claude-agent-sdk"
    )
    import json

    settings = json.loads((tmp_path / ".claude" / "settings.json").read_text(encoding="utf-8"))
    assert settings["env"]["AAMAD_TARGET_RUNTIME"] == "claude-agent-sdk"
    assert (tmp_path / ".env").read_text(encoding="utf-8").count(
        "AAMAD_TARGET_RUNTIME=claude-agent-sdk"
    ) == 1
