"""AFK Telegram Bot Module.

This module implements an AFK (Away From Keyboard) feature for Telegram users.

Main features:
- `.afk [message]` — activates AFK mode with an optional message.
- `.unafk` — deactivates AFK mode and reports how long the user was AFK.
- Automatically replies to private messages while AFK with a custom message.
"""

import argparse
from datetime import datetime
from zoneinfo import ZoneInfo

from loguru import logger
from telethon import TelegramClient, events
from telethon.events.newmessage import NewMessage
from telethon.tl.types import PeerUser

from app.config import config
from app.state import BotState, load_state, save_state
from app.utils import format_duration, setup_logger

# Initialize the Telegram client with credentials from config
client: TelegramClient = TelegramClient(
    session=config.session_name, api_id=config.api_id, api_hash=config.api_hash
)


@client.on(events.NewMessage(outgoing=True, pattern=r"\.afk\s*(.*)"))
async def start_afk_handler(event: NewMessage.Event) -> None:
    """Handle the `.afk` command.

    Activates AFK mode and optionally sets a custom AFK message.
    The bot stores the AFK state, including the start time and custom message.

    Args:
        event (NewMessage.Event): The incoming Telethon message event.

    Example:
        `.afk` → activates AFK without a message.
        `.afk busy now` → activates AFK with the message "busy now".
    """
    afk_message: str = event.pattern_match.group(1).strip()
    state: BotState = BotState(afk_message=afk_message, is_afk=True)
    save_state(state)

    logger.info(f"AFK mode activated with message: '{afk_message}'")

    # Build the response message
    response: str = "**AFK mode activated**"
    if afk_message:
        response += f"\nMessage: `{afk_message}`"

    await event.edit(response)


@client.on(events.NewMessage(outgoing=True, pattern=r"\.unafk"))
async def start_unafk_handler(event: NewMessage.Event) -> None:
    """Handle the `.unafk` command.

    Deactivates AFK mode if active, and shows the total AFK duration.

    Args:
        event (NewMessage.Event): The incoming Telethon message event.
    """
    state: BotState = load_state()

    if state.is_afk:
        state.is_afk = False
        save_state(state)

        # Calculate AFK duration
        afk_duration = datetime.now(tz=ZoneInfo(config.timezone)) - state.afk_start_time

        logger.info(f"AFK mode deactivated. Duration: {afk_duration}")
        await event.edit(
            "**AFK mode deactivated**"
            f"\nYou were AFK for `{format_duration(afk_duration)}`"
        )
    else:
        logger.warning("Attempted to deactivate AFK mode, but it was not active.")
        await event.edit("**AFK mode was not active**")


@client.on(events.NewMessage(incoming=True))
async def handle_private_message(event: NewMessage.Event) -> None:
    """Handle incoming private messages when AFK mode is active.

    If AFK mode is enabled, the bot automatically replies with:
    - the AFK reason (if provided)
    - the duration of the AFK period

    The bot ensures each user is only notified once per AFK session.

    Args:
        event (NewMessage.Event): The incoming Telethon message event.
    """
    # Process only private messages (ignore groups/channels)
    if not isinstance(event.peer_id, PeerUser):
        return

    sender_id: int = event.sender_id
    state: BotState = load_state()

    if not state.is_afk:
        logger.debug(f"No AFK reply sent to {sender_id} because AFK mode is inactive.")
        return

    # Avoid re-notifying the same user
    if sender_id in getattr(state, "notified_ids", []):
        logger.debug(f"User {sender_id} already notified about AFK status.")
        return

    state.notified_ids.append(sender_id)
    save_state(state)

    # Calculate how long the user has been AFK
    afk_duration = datetime.now(tz=ZoneInfo(config.timezone)) - state.afk_start_time

    # Build the AFK response message
    response: str = "**I am currently AFK**"
    if state.afk_message:
        response += f"\nReason: `{state.afk_message}`"
    response += f"\nDuration: `{format_duration(afk_duration)}`"

    logger.info(f"Sent AFK notification to user {sender_id}.")
    await event.reply(response)


def main() -> None:
    """Entry point of the AFK bot.

    Parses CLI arguments, sets up logging, starts the Telegram client,
    and listens for events until the user disconnects.

    CLI Arguments:
        --login : Only authorize the client and exit (without running the bot).
    """
    parser = argparse.ArgumentParser(description="Telegram AFK Bot")
    parser.add_argument(
        "--login", action="store_true", help="Authorize only, no full bot launch."
    )
    args = parser.parse_args()

    try:
        client.start()
        if args.login:
            client.disconnect()
            return

        setup_logger()
        logger.info("Bot started successfully.")
        client.run_until_disconnected()

    except Exception as e:
        logger.exception(f"Unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
