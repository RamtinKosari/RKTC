# - Import Required Libraries
from telethon.network import ConnectionTcpFull
from telethon import TelegramClient
import sqlite3
import asyncio
import ollama
from ollama import chat, embed, ChatResponse, ResponseError
import socks
import json
import time
import os

# - Telegram Account API ID
RKTC_API_ID = os.environ.get("RKTC_API_ID")
# - Telegram Account API Hash
RKTC_API_HASH = os.environ.get("RKTC_API_HASH")
# - Target Channel/Group
RKTC_TARGET_CHANNEL = 'https://t.me/GermanyComma'
# - Proxy Settings
RKTC_PROXY = (socks.SOCKS5, '127.0.0.1', 2080)
# - Language Model
RKTC_MODEL = "gemma3"
# - Language Model Options
RKTC_OPTIONS = {
    "temperature": 0.1,
    "top_p": 0.3
}
# - Data File
RKTC_DATA_FILE = 'germany_data.json'
# - Iteration Limit
RKTC_ITERATION_LIMIT = 100
# - Message Length Limit
RKTC_MIN_MESSAGE_LENGTH = 10
# - Agent Prompt
RKTC_PROMPT = """
You are a Telegram message classifier.

IMPORTANT RULES:
- The message language is Persian. Always answer in Persian.
- NEVER use any other language except Persian and the required English category name.
- NEVER output random words, symbols, tokens, or explanations.
- NEVER output markdown.
- NEVER output anything except the exact format below.

Your task:
Analyze the Telegram message and create or select a specific category.

Category rules:
- Categories represent the specific topic or user intent.
- Do NOT use broad categories like "Help & Advice", "Application", or "University".
- Create a new category only when no existing category matches.
- Category format MUST be:
    English Category Name

Examples:
Embassy Appointment
Document Translation
Account Problem
Admission Received
Application Deadline
Application Process

Existing Categories:
{}

Message:
{}

Return ONLY:

Category: English Category
Keywords: keyword1, keyword2, keyword3
"""
# - Ignored Words
RKTC_IGNORED_WORDS = [
    "باشه",
    "اوکی",
    "ok",
    "مرسی",
    "ممنون",
    "ممنونم",
    "حتما",
    "خوبه",
    "اهان",
    "آها",
    "نه",
    "بله"
]