# Loads stocks.json and returns typed config objects.
# All other modules import from here — never read stocks.json directly.

import json
import os
from pathlib import Path

from dotenv import load_dotenv

from .models import StockWatch

_STOCKS_FILE = Path(__file__).parent.parent / "stocks.json"

load_dotenv(Path(__file__).parent / ".env")

_DEFAULTS = {
    "poll_interval_seconds": 30,
    "news_fetch_interval_seconds": 300,
}


def load_config() -> tuple[list[StockWatch], dict, str]:
    with open(_STOCKS_FILE) as f:
        data = json.load(f)

    stocks = [StockWatch(**s) for s in data["stocks"]]
    settings = {**_DEFAULTS, **data.get("settings", {})}

    api_key = os.environ["FINNHUB_API_KEY"]
    return stocks, settings, api_key


def load_pushover_keys() -> tuple[str | None, str | None]:
    token = os.environ.get("PUSHOVER_API_KEY") or None
    user_key = os.environ.get("PUSHOVER_USER_KEY") or None
    return token, user_key
