# 😴 AFK Telegram Bot

A lightweight Telegram userbot that implements an AFK (Away From Keyboard) status. Automatically replies to private messages while you're away and tracks how long you've been AFK.

## 📦 Requirements

* [Python 3.13+](https://www.python.org/downloads/)
* [Poetry](https://python-poetry.org/docs/#installation)
* [Task](https://taskfile.dev/) *(optional, for task automation)*
* A **Telegram account** (this is a **userbot**, not a regular bot)

## ⚙️ Setup

### 1. Clone the Repository

```bash
git clone https://github.com/NKTKLN/telegram-afk-bot
cd telegram-afk-bot
```

### 2. Install Dependencies

```bash
poetry install --no-root
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
API_ID=123456789
API_HASH=your_api_hash_here
SESSION_NAME=afk_bot              # Optional, defaults to config value
TIMEZONE=Europe/Moscow            # Optional, defaults to UTC
DB_PATH=bot_state.json            # Optional, where AFK state is saved
LOG_LEVEL=INFO                    # Optional
```

> You can get your API credentials here: [https://my.telegram.org/](https://my.telegram.org/)

### 4. Log In to Telegram

```bash
poetry run python -m app.main --login
```

You’ll be prompted to enter:

* Your phone number
* The verification code sent to Telegram
* (Optional) 2FA password

This creates a session file (e.g., `afk_bot.session`).

### 5. Start the Bot

```bash
poetry run python -m app.main
```

The bot will now listen for commands and handle private messages.

## 🐳 Run with Docker

### 1. Build the Docker Image

```bash
docker build -t telegram-afk-bot .
```

### 2. First-Time Login (Creates Session File)

```bash
docker run -it -v $(pwd):/app telegram-afk-bot --login
```

> This mounts the current directory so the session and state files are saved locally.

### 3. Run the Bot (Session Exists)

```bash
docker run -v $(pwd):/app telegram-afk-bot
```

### 4. Using Docker Compose

```bash
docker compose up --build -d
```

## 💬 Bot Commands

| Command | Description |
|--------|-------------|
| `.afk` | Enable AFK mode (no message) |
| `.afk I'm in a meeting` | Enable AFK with custom reason |
| `.unafk` | Disable AFK and show duration |

> Replies are sent **only in private chats**  
> Each user gets **one AFK notification** per session

## 📊 State Management

The bot saves its state (AFK status, start time, notified users) in `bot_state.json` (configurable via `DB_PATH`).

Example:

```json
{
  "is_afk": true,
  "afk_message": "sleeping",
  "afk_start_time": "2025-10-30T15:30:45.123456+03:00",
  "notified_ids": [123456789, 987654321]
}
```

## 📝 License

This project is licensed under the **MIT License**. See the [LICENSE.md](./LICENSE.md) file for more information.
