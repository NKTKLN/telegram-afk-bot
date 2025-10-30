"""Configuration module for the Telegram AFK Bot.

This module defines the `Config` class, which handles loading and validating
environment-based configuration using `pydantic-settings`.

It automatically loads values from:
- Environment variables
- A `.env` file (if present)

Example `.env` file:
    API_ID=123456
    API_HASH=abcd1234efgh5678
    SESSION_NAME=my-afk-bot
    TIMEZONE=Europe/Berlin
    DB_PATH=bot_state.json
    LOG_LEVEL=DEBUG
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Application configuration class for the Telegram AFK bot.

    Attributes:
        api_id (int): Telegram API ID obtained from https://my.telegram.org.
        api_hash (str): Telegram API hash key corresponding to `api_id`.
        session_name (str): The name of the Telethon session file (default: "afk_bot").
        timezone (str): The timezone name (default: "UTC").
        db_path (str): Path to the JSON file used to persist AFK state
            (default: "bot_state.json").
        log_level (str): Logging level (e.g., "INFO", "DEBUG", "WARNING").
        log_format (str): The Loguru-compatible format string for console output.
        model_config (SettingsConfigDict): Configuration settings for Pydantic.
    """

    api_id: int = Field(..., description="Telegram API ID.")
    api_hash: str = Field(..., description="Telegram API hash.")
    session_name: str = Field(
        default="afk_bot", description="Telethon session file name."
    )
    timezone: str = Field(
        default="UTC", description="Timezone for date/time operations."
    )
    db_path: str = Field(
        default="bot_state.json", description="Path to the AFK state file."
    )
    log_level: str = Field(default="INFO", description="Logging level for the bot.")

    # Loguru format string for logging messages
    log_format: str = (
        "<cyan>[{time:DD/MM/YY HH:mm:ss}]</cyan> "
        "<light-magenta>[{file}:{function}:{line}]</light-magenta> "
        "<lvl>[{level}]</lvl> - {message}"
    )

    # Pydantic settings configuration
    model_config = SettingsConfigDict(
        env_file=".env",  # Load environment variables from .env file
        env_prefix="",  # No prefix (can be added if needed)
        extra="ignore",  # Ignore extra environment variables
    )

    _ = model_config


# Initialize configuration on module import
config: Config = Config()
