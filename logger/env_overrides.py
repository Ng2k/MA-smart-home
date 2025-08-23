"""
@description: Apply environment variable overrides to logging configuration.
@author: Nicola Guerra
"""

import os
from typing import Any, Dict


def apply_env_level_overrides(cfg: Dict[str, Any]) -> None:
    """Apply env var overrides to a logging config dict.

    Supported:
      - LOG_LEVEL_ROOT=INFO
      - LOG_LEVEL_<LOGGERNAME>=DEBUG  (LOG_LEVEL_MYAPP_API -> 'myapp.api')
      - LOG_CONSOLE_LEVEL=WARNING     (console handler level)
    """

    def _norm(level: str) -> str:
        return level.strip().upper()

    root_level = os.getenv("LOG_LEVEL_ROOT")
    if root_level:
        cfg.setdefault("root", {})["level"] = _norm(root_level)

    # LOG_LEVEL_MYAPP, LOG_LEVEL_MYAPP_API, etc.
    for k, v in os.environ.items():
        if not k.startswith("LOG_LEVEL_") or k == "LOG_LEVEL_ROOT":
            continue
        # LOG_LEVEL_MYAPP_API -> myapp.api
        lname = k[len("LOG_LEVEL_"):].lower().replace("__", ".").replace("_", ".")
        loggers = cfg.setdefault("loggers", {})
        logger_cfg = loggers.setdefault(
            lname, {"handlers": ["console"], "propagate": False}
        )
        logger_cfg["level"] = _norm(v)

    console_level = os.getenv("LOG_CONSOLE_LEVEL")

    if not console_level:
        return
    handlers = cfg.setdefault("handlers", {})

    if "console" not in handlers:
        return
    handlers["console"]["level"] = _norm(console_level)
