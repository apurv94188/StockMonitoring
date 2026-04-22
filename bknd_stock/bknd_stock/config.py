import json
from pathlib import Path

from .models import StockWatch

_STOCKS_FILE = Path(__file__).parent.parent / "stocks.json"

_DEFAULTS = {
    "poll_interval_seconds": 30,
    "news_fetch_interval_seconds": 300,
}


def load_config() -> tuple[list[StockWatch], dict]:
    with open(_STOCKS_FILE) as f:
        data = json.load(f)

    stocks = [StockWatch(**s) for s in data["stocks"]]
    settings = {**_DEFAULTS, **data.get("settings", {})}
    return stocks, settings
