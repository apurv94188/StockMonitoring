import feedparser

from .models import NewsItem, StockWatch

_YAHOO_RSS = "https://finance.yahoo.com/rss/headline?s={ticker}"
_REUTERS_RSS = "https://feeds.reuters.com/reuters/businessNews"

_MAX_PER_TICKER = 5
_MAX_REUTERS = 3


def _keyword_matches(text: str, stock: StockWatch) -> bool:
    text_lower = text.lower()
    if stock.ticker.lower() in text_lower:
        return True
    for part in stock.name.lower().split():
        if len(part) > 3 and part in text_lower:
            return True
    return False


def fetch_news(stocks: list[StockWatch]) -> list[NewsItem]:
    items: list[NewsItem] = []
    seen: set[str] = set()

    for stock in stocks:
        url = _YAHOO_RSS.format(ticker=stock.ticker)
        feed = feedparser.parse(url)
        count = 0
        for entry in feed.entries:
            if count >= _MAX_PER_TICKER:
                break
            link = getattr(entry, "link", "")
            if link in seen:
                continue
            seen.add(link)
            items.append(
                NewsItem(
                    title=entry.get("title", ""),
                    link=link,
                    published=entry.get("published", ""),
                    source="Yahoo Finance",
                    ticker=stock.ticker,
                )
            )
            count += 1

    reuters_feed = feedparser.parse(_REUTERS_RSS)
    if reuters_feed.entries:
        for entry in reuters_feed.entries:
            link = getattr(entry, "link", "")
            if link in seen:
                continue
            title = entry.get("title", "")
            matched = next((s for s in stocks if _keyword_matches(title, s)), None)
            if matched is None:
                continue
            seen.add(link)
            items.append(
                NewsItem(
                    title=title,
                    link=link,
                    published=entry.get("published", ""),
                    source="Reuters",
                    ticker=matched.ticker,
                )
            )
            if sum(1 for i in items if i.source == "Reuters") >= _MAX_REUTERS:
                break

    return items
