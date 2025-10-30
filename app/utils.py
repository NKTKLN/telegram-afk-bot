"""Logging and Utility Module.

This module configures the application logger using `loguru` and provides
a helper function to format `datetime.timedelta` objects into a human-readable
string (e.g., "2d 3h 15m").

Features:
- Centralized logger setup with configurable format and level from `config`.
- Duration formatting for AFK uptime or similar time intervals.
"""

import sys
from datetime import timedelta

from loguru import logger

from app.config import config


def setup_logger() -> None:
    """Initialize and configure the global logger.

    Removes the default handler and adds a new one writing to stdout with
    settings defined in `config` (format, level, color, etc.).
    """
    logger.remove()

    logger.add(
        sys.stdout,
        format=config.log_format,
        level=config.log_level,
        colorize=True,
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

    logger.info("Logging initialized")
    logger.info(f"Logging level set to: {config.log_level}")


def format_duration(td: timedelta) -> str:
    """Convert a `timedelta` object into a compact human-readable string.

    Example:
        >>> format_duration(timedelta(days=2, hours=3, minutes=15))
        '2d 3h 15m'

    Args:
        td (timedelta): The time difference to format.

    Returns:
        str: Formatted duration using `d`, `h`, and `m` suffixes.
             Minutes are always shown if no larger units are present.
    """
    total_seconds: int = int(td.total_seconds())
    days, remainder = divmod(total_seconds, 86_400)  # seconds in a day
    hours, remainder = divmod(remainder, 3_600)  # seconds in an hour
    minutes, _ = divmod(remainder, 60)

    parts: list[str] = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0 or not parts:  # show minutes if it's the only unit
        parts.append(f"{minutes}m")

    return " ".join(parts)
