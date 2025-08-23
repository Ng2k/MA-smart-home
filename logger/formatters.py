"""
@description: color-aware logging formatters for the logger package.
@author: Nicola Guerra
"""

from __future__ import annotations

import logging
import sys
from typing import Optional


class ColorFormatter(logging.Formatter):
    """A simple ANSI color formatter.

    Usage from dictConfig:
      formatters:
        color:
          (): logger.formatters.ColorFormatter
          format: '%(levelname)s: %(message)s'
          use_colors: True
    """

    # Color Palette
    COLOR_MAP = {
        "DEBUG": "\x1b[34m",  # blue
        "INFO": "\x1b[36m",  # cyan
        "WARNING": "\x1b[33m",  # yellow
        "ERROR": "\x1b[31m",  # red
        "CRITICAL": "\x1b[35m",  # magenta
    }
    RESET = "\x1b[0m"

    # Additional colors for other parts
    TIMESTAMP_COLOR = "\x1b[90m"  # bright black / dim
    LOGGER_NAME_COLOR = "\x1b[32m"  # green

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        use_colors: Optional[bool] = None,
        color_timestamp: Optional[bool] = True,
        color_logger_name: Optional[bool] = True,
        color_message: Optional[bool] = False,
    ):
        super().__init__(fmt=fmt, datefmt=datefmt)
        if use_colors is None:
            # autodetect TTY on stderr/stdout
            self.use_colors = (
                hasattr(sys.stderr, "isatty") and sys.stderr.isatty()
            ) or (hasattr(sys.stdout, "isatty") and sys.stdout.isatty())
        else:
            self.use_colors = bool(use_colors)
        # feature flags
        self.color_timestamp = bool(color_timestamp)
        self.color_logger_name = bool(color_logger_name)
        self.color_message = bool(color_message)

    def format(self, record: logging.LogRecord) -> str:
        msg = super().format(record)
        if not self.use_colors:
            return msg
        color = self.COLOR_MAP.get(record.levelname, "")
        if not color:
            return msg

        out = msg

        # Color timestamp if present (naive: match ISO-like prefix)
        if self.color_timestamp and self.datefmt and out.startswith("20"):
            parts = out.split(" ", 1)
            if len(parts) == 2:
                out = f"{self.TIMESTAMP_COLOR}{parts[0]}{self.RESET} {parts[1]}"

        # Color logger name if present in format
        if self.color_logger_name and record.name and record.name in out:
            out = out.replace(
                record.name, f"{self.LOGGER_NAME_COLOR}{record.name}{self.RESET}"
            )

        # Color level
        level = record.levelname
        if level in out:
            out = out.replace(level, f"{color}{level}{self.RESET}")

        # Optionally color the message payload
        if self.color_message:
            # naive: color after the level name
            if level in out:
                before, _, after = out.partition(f"{color}{level}{self.RESET}")
                out = (
                    f"{before}{color}{level}"
                    f"{self.RESET}{self.COLOR_MAP.get('INFO', '')}{after}{self.RESET}"
                )

        return out


def from_config(
    format: Optional[str] = None,
    datefmt: Optional[str] = None,
    use_colors: Optional[bool] = None,
    color_timestamp: Optional[bool] = True,
    color_logger_name: Optional[bool] = True,
    color_message: Optional[bool] = False,
) -> ColorFormatter:
    """Factory used by dictConfig: returns a configured ColorFormatter.
    dictConfig will call this factory with keywords inside the formatter dict.

    :param format: The log message format string.
    :param datefmt: The date/time format string.
    :param use_colors: Whether to use colors in the output.
    :param color_timestamp: Whether to color the timestamp.
    :param color_logger_name: Whether to color the logger name.
    :param color_message: Whether to color the message.
    :return: A configured ColorFormatter instance.
    """
    return ColorFormatter(
        fmt=format,
        datefmt=datefmt,
        use_colors=use_colors,
        color_timestamp=color_timestamp,
        color_logger_name=color_logger_name,
        color_message=color_message,
    )
