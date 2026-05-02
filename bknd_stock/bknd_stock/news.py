# Fetches news from Yahoo Finance RSS (per-ticker) and Reuters (general business feed).
# Called on a slower interval than price polling (default every 5 minutes).

import feedparser

from .models import NewsItem, StockWatch

# Yahoo Finance provides a per-ticker RSS endpoint — substitute {ticker} before fetching
_YAHOO_RSS = "https://finance.yahoo.com/rss/headline?s={ticker}"
_REUTERS_RSS = "https://feeds.reuters.com/reuters/businessNews"

# Cap how many articles we keep per source to avoid flooding the UI
_MAX_PER_TICKER = 5   # Max Yahoo Finance articles per stock
_MAX_REUTERS = 3      # Max Reuters articles across all stocks


def _keyword_matches(text: str, stock: StockWatch) -> bool:
    # Returns True if the article text mentions the ticker symbol or any significant
    # word from the company name (words longer than 3 chars to skip "Inc", "the", etc.)
    text_lower = text.lower()
    if stock.ticker.lower() in text_lower:
        return True
    for part in stock.name.lower().split():
        if len(part) > 3 and part in text_lower:
            return True
    return False


def fetch_news(stocks: list[StockWatch]) -> list[NewsItem]:
    items: list[NewsItem] = []
    seen: set[str] = set()  # Track article URLs to avoid duplicates across sources

    # --- Yahoo Finance (per-ticker RSS) ---
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
                    ticker=stock.ticker,  # Known because we fetched from this ticker's feed
                )
            )
            count += 1

    # --- Reuters (general feed — keyword-match to assign a ticker) ---
    reuters_feed = feedparser.parse(_REUTERS_RSS)
    if reuters_feed.entries:
        for entry in reuters_feed.entries:
            link = getattr(entry, "link", "")
            if link in seen:
                continue
            title = entry.get("title", "")
            # Find the first stock whose name/ticker appears in the headline
            matched = next((s for s in stocks if _keyword_matches(title, s)), None)
            if matched is None:
                continue  # Skip Reuters articles that don't relate to any watched stock
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
            # Stop once we've collected enough Reuters articles
            if sum(1 for i in items if i.source == "Reuters") >= _MAX_REUTERS:
                break

    return items
