"""
@description: Unit tests for the logger configuration module.
@author: Nicola Guerra
"""

import importlib.resources as resources
import io
from pathlib import Path

import pytest
import yaml

from logger.config import load_config

SIMPLE_YAML = "a: 1\nb:\n  - 2\n  - 3\n"


def test_load_default_uses_packaged_resource(monkeypatch):
    # make resources.open_text return our YAML without touching the FS
    def fake_open_text(package, resource, encoding="utf-8"):
        return io.StringIO(SIMPLE_YAML)

    monkeypatch.setattr(resources, "open_text", fake_open_text)
    cfg = load_config(None)
    assert cfg == {"a": 1, "b": [2, 3]}


def test_load_from_str_path(tmp_path: Path):
    p = tmp_path / "cfg.yml"
    p.write_text(SIMPLE_YAML, encoding="utf-8")
    cfg = load_config(str(p))
    assert cfg["a"] == 1 and cfg["b"] == [2, 3]


def test_load_from_pathlib_path(tmp_path: Path):
    p = tmp_path / "cfg.yaml"
    p.write_text(SIMPLE_YAML, encoding="utf-8")
    cfg = load_config(p)
    assert cfg == {"a": 1, "b": [2, 3]}


def test_missing_file_raises_file_not_found(tmp_path: Path):
    p = tmp_path / "nope.yml"
    with pytest.raises(FileNotFoundError):
        load_config(p)


def test_unsupported_extension_raises_value_error(tmp_path: Path):
    p = tmp_path / "cfg.txt"
    p.write_text("k: v", encoding="utf-8")
    with pytest.raises(ValueError):
        load_config(p)


def test_invalid_yaml_propagates_yaml_error(tmp_path: Path):
    p = tmp_path / "bad.yml"
    p.write_text("bad: [unclosed", encoding="utf-8")
    with pytest.raises(yaml.YAMLError):
        load_config(p)
