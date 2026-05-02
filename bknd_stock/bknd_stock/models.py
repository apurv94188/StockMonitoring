# Shared data models used across the backend.
# Using dataclasses keeps things lightweight — no ORM or validation library needed.

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class StockWatch:
    ticker: str
    name: str
    alert_threshold_pct: float = 1.0
    current_price: float | None = None
    previous_closed_price: float | None = None
    day_max_price: float | None = None
    day_min_price: float | None = None
    day_open_price: float | None = None
    change_pct: float | None = None
    current_price_timestamp: datetime | None = None

    def __str__(self) -> str:
        price = f"${self.current_price:.2f}" if self.current_price is not None else "—"
        prev = f"${self.previous_closed_price:.2f}" if self.previous_closed_price is not None else "—"
        return f"{self.name} ({self.ticker}) | current: {price} | prev close: {prev} | ts: {self.current_price_timestamp}"
    


@dataclass
class PriceAlert:
    # Created by monitor.detect_alerts() when a price moves past the threshold
    ticker: str
    name: str
    current_price: float
    previous_closed_price: float
    change_pct: float                           # Positive = up, negative = down w.r.t. previous_closed_price
    timestamp: datetime = field(default_factory=datetime.now)  # Time the alert fired


@dataclass
class NewsItem:
    # One article returned by news.fetch_news()
    title: str
    link: str
    published: str   # Raw string from RSS feed — format varies by source
    source: str      # e.g. "Yahoo Finance" or "Reuters"
    ticker: str | None = None  # None for Reuters items that matched by keyword only
