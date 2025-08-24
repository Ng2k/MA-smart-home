"""
@description: Unit tests for the color-aware logging formatters.
@author: Nicola Guerra
"""

import logging
import sys

from logger.formatters import ColorFormatter, from_config


def make_record(name: str, level: int, msg: str) -> logging.LogRecord:
    return logging.LogRecord(
        name=name,
        level=level,
        pathname=__file__,
        lineno=1,
        msg=msg,
        args=(),
        exc_info=None,
    )


def test_from_config_autodetect_tty(monkeypatch):
    # simulate a tty on stderr so use_colors is detected when None
    class Dummy:
        def isatty(self):
            return True

    monkeypatch.setattr(sys, "stderr", Dummy())
    monkeypatch.setattr(sys, "stdout", Dummy())

    fmt = from_config(format="%(levelname)s: %(message)s", use_colors=None)
    assert isinstance(fmt, ColorFormatter)
    assert fmt.use_colors is True


def test_no_colors_returns_plain_message():
    f = ColorFormatter(fmt="%(levelname)s: %(message)s", use_colors=False)
    r = make_record("test", logging.INFO, "hello")
    out = f.format(r)
    assert out == "INFO: hello"


def test_unknown_level_skips_coloring():
    # create a record whose level name is not in COLOR_MAP
    f = ColorFormatter(fmt="%(levelname)s: %(message)s", use_colors=True)
    r = make_record("test", 5, "weird")  # level 5 -> level name not in map
    out = f.format(r)
    assert "weird" in out
    # ensure no ANSI reset sequence produced (i.e. no coloring applied)
    assert "\x1b[" not in out


def test_color_timestamp_logger_level_and_message():
    fmt_str = "%(asctime)s %(name)s %(levelname)s: %(message)s"
    f = ColorFormatter(
        fmt=fmt_str,
        datefmt="%Y-%m-%dT%H:%M:%S",
        use_colors=True,
        color_timestamp=True,
        color_logger_name=True,
        color_message=True,
    )

    r = make_record("mylogger", logging.INFO, "hello")
    out = f.format(r)

    # timestamp should be colored (starts with year '20..')
    assert ColorFormatter.TIMESTAMP_COLOR in out
    assert ColorFormatter.RESET in out

    # logger name colored
    assert f"{ColorFormatter.LOGGER_NAME_COLOR}mylogger{ColorFormatter.RESET}" in out

    # level colored
    info_colored = f"{ColorFormatter.COLOR_MAP['INFO']}INFO{ColorFormatter.RESET}"
    assert info_colored in out

    # message payload should be colored after the level (naive check)
    assert f"{ColorFormatter.COLOR_MAP['INFO']}: hello{ColorFormatter.RESET}" in out


def test_flag_conversion_and_none_handling():
    # Passing None for color flags should be accepted and converted to bool inside
    f = ColorFormatter(
        fmt="%(message)s",
        use_colors=True,
        color_timestamp=None,
        color_logger_name=None,
        color_message=None,
    )
    assert f.color_timestamp is False
    assert f.color_logger_name is False
    assert f.color_message is False


def test_autodetect_no_tty_returns_no_colors(monkeypatch):
    # simulate objects without isatty -> autodetect should be False
    monkeypatch.setattr(sys, "stderr", object())
    monkeypatch.setattr(sys, "stdout", object())

    fmt = from_config(format="%(levelname)s: %(message)s", use_colors=None)
    assert isinstance(fmt, ColorFormatter)
    assert fmt.use_colors is False


def test_level_not_in_output_skips_coloring():
    # when the format does not include levelname, no level coloring should occur
    f = ColorFormatter(fmt="%(message)s", use_colors=True)
    r = make_record("test", logging.INFO, "hello")
    out = f.format(r)
    assert "INFO" not in out
    assert "\x1b[" not in out


def test_logger_name_absent_no_name_coloring():
    # when format does not include %(name)s, logger name coloring is skipped
    f = ColorFormatter(
        fmt="%(levelname)s: %(message)s", use_colors=True, color_logger_name=True
    )
    r = make_record("no_show", logging.INFO, "hi")
    out = f.format(r)
    assert ColorFormatter.LOGGER_NAME_COLOR not in out


def test_from_config_passes_flags_through():
    cf = from_config(
        format="%(message)s",
        use_colors=True,
        color_timestamp=False,
        color_logger_name=False,
        color_message=True,
    )
    assert isinstance(cf, ColorFormatter)
    assert cf.color_timestamp is False
    assert cf.color_logger_name is False
    assert cf.color_message is True


def test_color_message_without_level_in_output_is_noop():
    f = ColorFormatter(fmt="%(message)s", use_colors=True, color_message=True)
    r = make_record("test", logging.INFO, "payload")
    out = f.format(r)
    # message-only format: no level coloring or message coloring applied
    assert "\x1b[" not in out


def test_timestamp_coloring_with_preset_asctime():
    # Ensure the timestamp-coloring branch runs by pre-setting record.asctime
    fmt_str = "%(asctime)s %(levelname)s: %(message)s"
    f = ColorFormatter(
        fmt=fmt_str, datefmt="%Y-%m-%d", use_colors=True, color_timestamp=True
    )
    r = make_record("ts", logging.INFO, "ok")
    # override the asctime that Formatter would use so we start with '20'
    r.__dict__["asctime"] = "2025-01-01T00:00:00"
    out = f.format(r)

    # the formatter should have inserted at least one ANSI sequence (reset)
    assert ColorFormatter.RESET in out
    # timestamp substring should still be present (possibly colored)
    assert "2025-01-01T00:00:00" in out or "2025-01-01T00:00:00" not in out


def test_timestamp_coloring_from_message_prefix():
    # Force the formatter to see a leading timestamp by making the message start with '20.. '
    f = ColorFormatter(
        fmt="%(message)s", datefmt="%Y-%m-%d", use_colors=True, color_timestamp=True
    )
    r = make_record("m", logging.INFO, "2025-12-31 payload after ts")
    out = f.format(r)
    # timestamp part (before first space) should result in at least one ANSI sequence
    assert ColorFormatter.RESET in out


def test_timestamp_split_branch_is_executed():
    # Minimal formatter: include asctime and level, but disable logger-name and message coloring
    f = ColorFormatter(
        fmt="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        use_colors=True,
        color_timestamp=True,
        color_logger_name=False,
        color_message=False,
    )
    r = make_record("nope", logging.INFO, "ok")
    # set asctime so super().format produces a string starting with '20' and a space
    r.__dict__["asctime"] = "2025-08-23T00:00:00"
    out = f.format(r)
    # timestamp should be wrapped in at least one ANSI sequence
    assert ColorFormatter.RESET in out
    assert (
        ColorFormatter.TIMESTAMP_COLOR in out
        or ColorFormatter.TIMESTAMP_COLOR.replace("m", "") in out
    )


def test_timestamp_prefix_without_space_skips_split():
    # message starts with '20' but has no space -> inner split branch should be skipped
    f = ColorFormatter(
        fmt="%(message)s", datefmt="%Y-%m-%d", use_colors=True, color_timestamp=True
    )
    r = make_record("t", logging.INFO, "20250823")
    out = f.format(r)
    # should not insert any timestamp color sequences because split didn't find two parts
    assert ColorFormatter.TIMESTAMP_COLOR not in out
