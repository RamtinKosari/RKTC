# RKTC

**Ramtin Kosari Telegram Crawler** — a Python tool that fetches messages from a Telegram channel, classifies them into categories using a local Ollama LLM, and provides a simple web dashboard for browsing the results.

## Features

- **Crawl** messages from a Telegram channel
- **Categorize** Persian messages with a local LLM
- **Normalize** category names to avoid duplicates
- **Classify** categories by project purpose (main vs. other topics)
- **Thread replies** under their parent messages
- **Web dashboard** with:
  - Category selection + category search
  - Main categories list + "Other Topics" accordion
  - Keyword search
  - Date range filter
  - Combined multi-category timeline
  - Light / dark theme (gray zinc palette)
  - Chat-bubble message view (different styling for main/reply messages)

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
- Project purpose (`RKTC_PURPOSE`) — categories are classified as "main" or "other" relative to this purpose
- Proxy settings (`RKTC_PROXY`)
- Classification prompt (`RKTC_PROMPT`)
- Purpose-check prompt (`RKTC_PURPOSE_PROMPT`)

## Usage

Run the crawler:

```bash
python3 Crawler.py
```

The crawler will:

1. Load existing `messages.json` and `categories.json`
2. Classify any categories that are missing a purpose type
3. Fetch new messages from the configured channel
4. Classify each message with the local LLM
5. Save the results to `messages.json`, `categories.json`, and `category_messages.json`

## Dashboard

Start the dashboard server:

```bash
python3 dashboard/server.py
```

Open http://localhost:8040 in your browser.

Use the sidebar to select categories, search categories, search messages, filter by date range, and toggle the light/dark theme. Categories related to the configured purpose are shown in the main list; unrelated categories are collapsed under **Other Topics**.

To use a different port:

```bash
RKTC_DASHBOARD_PORT=8080 python3 dashboard/server.py
```

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
