# 💱 Currency Telegram Bot

An asynchronous Telegram bot that fetches live USD/EUR → UAH exchange rates using the [Monobank public API](https://api.monobank.ua/).

## Tech Stack

| Tool | Purpose |
|---|---|
| `aiogram` 3.x | Telegram bot framework |
| `aiohttp` | Async HTTP client |
| `python-dotenv` | Environment variable management |
| `uv` | Dependency & virtual-env management |
| `pytest` / `pytest-asyncio` / `pytest-mock` | Testing |

## Getting Started

### 1. Clone the repo

```bash
git clone <repo-url>
cd currency-telegram-bot
```

### 2. Create your `.env` file

```bash
cp .env.example .env
# Fill in BOT_TOKEN with your Telegram bot token from @BotFather
```

### 3. Create the virtual environment and install dependencies

```bash
uv sync --all-extras
```

### 4. Run the bot

```bash
uv run python -m bot.main
```

### 5. Run tests

```bash
uv run pytest
```

## Docker Deployment

You can deploy the bot using Docker and Docker Compose. This is the recommended way to run the bot on a remote server.

### 1. Clone the repository
```bash
git clone https://github.com/khomych-dev/currency-telegram-bot.git
cd currency-telegram-bot
```

### 2. Configure environment variables
```bash
cp .env.example .env
# Edit .env and add your BOT_TOKEN
```

### 3. Build and run the container
```bash
docker compose up -d --build
```
*(Note: If your server uses the older `docker-compose` standalone tool, use `docker-compose up -d --build` instead).*

## Project Structure

```
currency-telegram-bot/
├── bot/
│   ├── __init__.py
│   ├── main.py          # Entry point — bot setup & polling
│   ├── handlers.py      # Telegram message/command handlers
│   └── api.py           # Monobank API client & rate parsing
├── tests/
│   ├── __init__.py
│   ├── test_api.py      # Tests for API parsing logic
│   └── test_handlers.py # Tests for handler message formatting
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```
