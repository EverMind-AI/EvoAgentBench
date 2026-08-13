import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest
import yaml

import config as config_module


def _reload_config():
    return importlib.reload(config_module)


def _write_yaml(path: Path, payload: dict) -> None:
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")


def test_missing_agent_config_fails_instead_of_switching_agent(tmp_path):
    config_path = tmp_path / "config.yaml"
    _write_yaml(
        config_path,
        {
            "agent_configs": {"nanobot": "./nanobot.yaml"},
            "agent": "nanobot",
            "domain": {"name": "information_retrieval"},
        },
    )

    config = _reload_config()
    with pytest.raises(FileNotFoundError, match="Agent config not found"):
        config.load_config(str(config_path))


def test_selected_agent_is_loaded_from_its_yaml(tmp_path):
    agent_path = tmp_path / "nanobot.yaml"
    _write_yaml(agent_path, {"name": "nanobot", "command": "nanobot"})
    config_path = tmp_path / "config.yaml"
    _write_yaml(
        config_path,
        {
            "agent_configs": {"nanobot": "./nanobot.yaml"},
            "agent": "nanobot",
            "domain": {"name": "information_retrieval"},
            "job_dir": "./jobs",
        },
    )

    config = _reload_config()
    loaded = config.load_config(str(config_path))

    assert loaded["agent"]["name"] == "nanobot"
    assert loaded["job_dir"] == str((tmp_path / "jobs").resolve())


def test_relative_path_with_spaces_is_resolved(tmp_path):
    config = _reload_config()
    resolved = config._resolve("./Knowledge Work/meta_prompts", tmp_path)

    assert resolved == str((tmp_path / "Knowledge Work" / "meta_prompts").resolve())
