# Shared data models used across the backend.
# Using dataclasses keeps things lightweight — no ORM or validation library needed.

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class PctThreshold:
    threshold: float          # % change vs. previous close that triggers the alert
    buffer: float = 0.0       # Price must retreat this many % past threshold before re-arming


@dataclass
class PriceLevelAlert:
    level: float              # Absolute price level that triggers the alert
    buffer: float = 0.0       # Price must retreat this many $ past level before re-arming


@dataclass
class StockWatch:
    ticker: str
    name: str
    # Multiple % change thresholds vs. previous close — each fires independently
    alert_pct_thresholds: list[PctThreshold] = field(default_factory=list)
    # Price-level alerts — fire when price crosses the level in the given direction
    alert_price_above: list[PriceLevelAlert] = field(default_factory=list)
    alert_price_below: list[PriceLevelAlert] = field(default_factory=list)
    current_price: float | None = None
    previous_closed_price: float | None = None
    day_max_price: float | None = None
    day_min_price: float | None = None
    day_open_price: float | None = None
    change_pct: float | None = None
    current_price_timestamp: datetime | None = None

    def __post_init__(self):
        # Convert raw dicts from JSON into typed threshold objects
        self.alert_pct_thresholds = [
            PctThreshold(**t) if isinstance(t, dict) else t
            for t in self.alert_pct_thresholds
        ]
        self.alert_price_above = [
            PriceLevelAlert(**t) if isinstance(t, dict) else t
            for t in self.alert_price_above
        ]
        self.alert_price_below = [
            PriceLevelAlert(**t) if isinstance(t, dict) else t
            for t in self.alert_price_below
        ]

    def __str__(self) -> str:
        price = f"${self.current_price:.2f}" if self.current_price is not None else "—"
        prev = f"${self.previous_closed_price:.2f}" if self.previous_closed_price is not None else "—"
        return f"{self.name} ({self.ticker}) | current: {price} | prev close: {prev} | ts: {self.current_price_timestamp}"


@dataclass
class PriceAlert:
    # Created by monitor.detect_alerts() when a price moves past a threshold
    ticker: str
    name: str
    current_price: float
    previous_closed_price: float
    change_pct: float        # Positive = up, negative = down vs. previous close
    alert_type: str          # "pct_up" | "pct_down" | "price_above" | "price_below"
    threshold: float         # The specific value that triggered this alert
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class NewsItem:
    # One article returned by news.fetch_news()
    title: str
    link: str
    published: str   # Raw string from RSS feed — format varies by source
    source: str      # e.g. "Yahoo Finance" or "Reuters"
    ticker: str | None = None  # None for Reuters items that matched by keyword only