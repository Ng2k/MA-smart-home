"""
@description: Factory module to create logger instances.
@author: Nicola Guerra
"""

import logging
import logging.config
from pathlib import Path
from threading import Lock
from typing import Optional

from .config import load_config
from .env_overrides import apply_env_level_overrides

_lock = Lock()


class Configurator:
    """Singleton-like configurator guarding reconfiguration."""

    _configured: bool = False

    @classmethod
    def init_logging(
        cls,
        config: Optional[Path] = None,
        *,
        allow_reconfigure: bool = True,
        apply_env_overrides: bool = True,
    ) -> None:
        """Initialize logging configuration.

        :param config: Optional path to a custom YAML config file.
        :param allow_reconfigure: Allow reconfiguration if already configured.
        :param apply_env_overrides: Apply environment variable overrides.
        :return: None
        """
        with _lock:
            if cls._configured and not allow_reconfigure:
                return
            cfg = load_config(config)
            if apply_env_overrides:
                apply_env_level_overrides(cfg)
            logging.config.dictConfig(cfg)
            cls._configured = True

    @classmethod
    def get_logger(cls, name: Optional[str] = None) -> logging.Logger:
        """Get a logger instance.

        :param name: Optional name of the logger.
        :return: Logger instance.
        """
        if not cls._configured:
            # apply safe default once
            cls.init_logging(allow_reconfigure=False)
        return logging.getLogger(name) if name else logging.getLogger()


# public API
def init_logging(
    config: Optional[Path] = None,
    *,
    allow_reconfigure: bool = True,
    apply_env_overrides: bool = True,
) -> None:
    """Initialize logging configuration.

    :param config: Optional path to a custom YAML config file.
    :param allow_reconfigure: Allow reconfiguration if already configured.
    :param apply_env_overrides: Apply environment variable overrides.
    :return: None
    """
    Configurator.init_logging(
        config,
        allow_reconfigure=allow_reconfigure,
        apply_env_overrides=apply_env_overrides,
    )


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance.

    :param name: Optional name of the logger.
    :return: Logger instance.
    """
    return Configurator.get_logger(name)
