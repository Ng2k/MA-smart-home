"""
@description: Load logging configuration from various sources.
@author: Nicola Guerra
"""

import importlib.resources as resources
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml


def load_config(source: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """Load logging configuration from a path or the packaged default YAML.

    :param source: Optional path to a custom YAML config file.
    :return: Logging configuration as a dictionary.
    """
    if source is None:
        with resources.open_text(
            "logger.configs", "default_config.yml", encoding="utf-8"
        ) as fh:
            return yaml.safe_load(fh)

    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"Logging config not found: {path}")

    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix in (".yml", ".yaml"):
        return yaml.safe_load(text)

    raise ValueError(f"Unsupported logging config extension: {suffix}")