"""
@description: Unit tests for the logger environment variable overrides.
@author: Nicola Guerra
"""

import copy
import os

import pytest

from logger.env_overrides import apply_env_level_overrides


def test_no_env_vars_no_change(monkeypatch):
    monkeypatch.delenv("LOG_LEVEL_ROOT", raising=False)
    monkeypatch.delenv("LOG_CONSOLE_LEVEL", raising=False)
    # ensure no accidental LOG_LEVEL_* set
    for k in list(os.environ.keys()):
        if k.startswith("LOG_LEVEL_"):
            monkeypatch.delenv(k, raising=False)

    cfg = {
        "formatters": {},
        "handlers": {},
        "loggers": {},
        "root": {"level": "WARNING"},
    }
    before = copy.deepcopy(cfg)
    apply_env_level_overrides(cfg)
    assert cfg == before


def test_root_level_set_and_stripped(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL_ROOT", " info ")
    cfg = {}
    apply_env_level_overrides(cfg)
    assert "root" in cfg and cfg["root"]["level"] == "INFO"


@pytest.mark.parametrize(
    "env_name,env_value,expected_logger",
    [
        ("LOG_LEVEL_MYAPP_API", "debug", "myapp.api"),
        ("LOG_LEVEL_MYAPP__API", "warning", "myapp.api"),
    ],
)
def test_logger_level_single_and_double_underscore(
    monkeypatch, env_name, env_value, expected_logger
):
    monkeypatch.setenv(env_name, env_value)
    cfg = {}
    apply_env_level_overrides(cfg)
    assert "loggers" in cfg
    assert expected_logger in cfg["loggers"]
    assert cfg["loggers"][expected_logger]["level"] == env_value.strip().upper()
    # default handlers and propagate must be set as in implementation
    assert cfg["loggers"][expected_logger]["handlers"] == ["console"]
    assert cfg["loggers"][expected_logger]["propagate"] is False


def test_console_level_updates_only_if_console_exists(monkeypatch):
    monkeypatch.setenv("LOG_CONSOLE_LEVEL", " error ")
    # Case 1: handlers exists and has console -> update
    cfg_with_console = {"handlers": {"console": {"level": "INFO"}}}
    apply_env_level_overrides(cfg_with_console)
    assert cfg_with_console["handlers"]["console"]["level"] == "ERROR"

    # Case 2: handlers exists but no console -> no crash and no console created
    cfg_no_console = {"handlers": {"file": {"level": "INFO"}}}
    apply_env_level_overrides(cfg_no_console)
    assert "console" not in cfg_no_console["handlers"]

    # Case 3: handlers missing entirely -> setdefault will create handlers but still not add console
    cfg_missing = {}
    apply_env_level_overrides(cfg_missing)
    assert cfg_missing.get("handlers") == {} or "console" not in cfg_missing["handlers"]


def test_existing_logger_config_preserved_and_level_overwritten(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL_MYAPP", "critical")
    cfg = {
        "loggers": {
            "myapp": {
                "level": "INFO",
                "handlers": ["file"],
                "propagate": True,
                "extra": "keep_me",
            }
        }
    }
    apply_env_level_overrides(cfg)
    # level overwritten
    assert cfg["loggers"]["myapp"]["level"] == "CRITICAL"
    # other keys preserved
    assert cfg["loggers"]["myapp"]["handlers"] == ["file"]
    assert cfg["loggers"]["myapp"]["propagate"] is True
    assert cfg["loggers"]["myapp"]["extra"]
