# RKTC

**Ramtin Kosari Telegram Crawler** — a Python tool that fetches messages from a Telegram channel, classifies them into categories using a local Ollama LLM, and provides a simple web dashboard for browsing the results.

## Features

- **Crawl** messages from a Telegram channel
- **Categorize** Persian messages with a local LLM
- **Normalize** category names to avoid duplicates
- **Thread replies** under their parent messages
- **Web dashboard** with:
  - Category selection
  - Keyword search
  - Date range filter
  - Combined multi-category timeline
  - Light / dark theme
  - Chat-bubble message view

## Requirements

- Python 3.10+
- Telegram API credentials (`api_id` and `api_hash` from [my.telegram.org](https://my.telegram.org))
- A running Ollama server with the configured model (default: `gemma3`)
- Optional: a SOCKS5 proxy at `127.0.0.1:2080` (can be disabled in `Configs.py`)

## Installation

Install the Python dependencies manually:

```bash
pip install telethon ollama PySocks
```

## Configuration

Set the required environment variables:

```bash
export RKTC_API_ID="your_api_id"
export RKTC_API_HASH="your_api_hash"
```

Edit `Configs.py` to change:

- Target channel (`RKTC_TARGET_CHANNEL`)
- Ollama model (`RKTC_MODEL`)
- Proxy settings (`RKTC_PROXY`)
- Classification prompt (`RKTC_PROMPT`)

## Usage

Run the crawler:

```bash
python3 Crawler.py
```

The crawler will:

1. Load existing `messages.json` and `categories.json`
2. Fetch new messages from the configured channel
3. Classify each message with the local LLM
4. Save the results to `messages.json`, `categories.json`, and `category_messages.json`

## Dashboard

Start the dashboard server:

```bash
python3 dashboard/server.py
```

Open http://localhost:8000 in your browser.

Use the sidebar to select categories, search messages, filter by date range, and toggle the light/dark theme.

## Data files

Generated at runtime:

| File | Description |
|------|-------------|
| `messages.json` | All fetched messages with category IDs |
| `categories.json` | Unique category list |
| `category_messages.json` | Messages grouped by category, with replies nested |
| `crawler_session.session` | Telethon session file |

These files are auto-generated and should not be committed.

## License

MIT License — Copyright (c) 2026 Ramtin Kosari
