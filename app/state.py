"""Bot State Management Module.

This module defines and manages the persistent AFK state of the Telegram bot.
It provides a Pydantic-based `BotState` model and utility functions to
save and load the state from a JSON file.

Stored information includes:
- Whether AFK mode is active
- The AFK message (if provided)
- The timestamp when AFK mode was activated
- The list of users who have already been notified

The state is persisted in a JSON file defined by `config.db_path`.
"""

import json
from datetime import datetime
from typing import List
from zoneinfo import ZoneInfo

from loguru import logger
from pydantic import BaseModel, Field

from app.config import config


class BotState(BaseModel):
    """Represents the current AFK state of the bot.

    Attributes:
        afk_message (str): Custom AFK message set by the user.
        notified_ids (List[int]): List of Telegram user IDs already notified.
        is_afk (bool): Whether the bot is currently in AFK mode.
        afk_start_time (datetime): The timestamp when AFK mode was activated.
    """

    afk_message: str = Field(
        default="", description="Optional AFK message displayed when replying to users."
    )
    notified_ids: List[int] = Field(
        default_factory=list,
        description="List of user IDs that were already notified about AFK status.",
    )
    is_afk: bool = Field(
        default=False, description="Indicates whether the bot is currently in AFK mode."
    )
    afk_start_time: datetime = Field(
        default_factory=lambda: datetime.now(tz=ZoneInfo(config.timezone)),
        description="Timestamp of when AFK mode was activated.",
    )


def save_state(state: BotState) -> None:
    """Save the bot's AFK state to a JSON file.

    Args:
        state (BotState): The current bot state to be persisted.
    """
    with open(config.db_path, "w", encoding="utf-8") as db_file:
        json.dump(state.model_dump(), db_file, ensure_ascii=False, default=str)


def load_state() -> BotState:
    """Load the bot's AFK state from a JSON file.

    Returns:
        BotState: The loaded bot state, or a new default state if loading fails.
    """
    try:
        with open(config.db_path, encoding="utf-8") as db_file:
            data: dict = json.load(db_file)

            # Convert AFK start time from string to datetime if necessary
            if "afk_start_time" in data and isinstance(data["afk_start_time"], str):
                try:
                    data["afk_start_time"] = datetime.fromisoformat(
                        data["afk_start_time"]
                    )
                except ValueError:
                    data["afk_start_time"] = datetime.now(tz=ZoneInfo(config.timezone))

            return BotState(**data)

    except (json.JSONDecodeError, ValueError, FileNotFoundError) as e:
        logger.warning(f"Failed to load state: {e}")
        return BotState()
