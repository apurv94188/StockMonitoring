from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class StockWatch:
    ticker: str
    name: str
    alert_threshold_pct: float = 1.0


@dataclass
class PriceAlert:
    ticker: str
    name: str
    current_price: float
    previous_price: float
    change_pct: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class NewsItem:
    title: str
    link: str
    published: str
    source: str
    ticker: str | None = None
