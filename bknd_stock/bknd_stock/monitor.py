import json
import urllib.request
import datetime
from .models import PriceAlert, StockWatch

_FINNHUB_QUOTE_URL = "https://finnhub.io/api/v1/quote?symbol={symbol}&token={token}"


def fetch_prices(stocks: list[StockWatch], api_key: str) -> list[StockWatch]:
    print("fetching the data for stocks")
    for stock in stocks:
        print("fetching ", stock.name)
        try:
            url = _FINNHUB_QUOTE_URL.format(symbol=stock.ticker, token=api_key)
            with urllib.request.urlopen(url, timeout=10) as resp:
                quote = json.loads(resp.read())
            # 'c' is current price; fall back to previous close 'pc' outside market hours
            price = quote.get("c") or quote.get("pc")
            if price:
                stock.current_price = float(quote.get("c")) or float(quote.get("pc"))
                stock.previous_closed_price = float(quote.get("pc"))
                stock.day_max_price = float(quote.get("h"))
                stock.day_min_price = float(quote.get("l"))
                stock.day_open_price = float(quote.get("o"))
                stock.current_price_timestamp = datetime.datetime.now()
            print(stock)
        except Exception:
            pass

    return stocks


def detect_alerts(
    stocks: list[StockWatch]
) -> list[PriceAlert]:
    # Build a ticker → StockWatch lookup so we can read each stock's threshold
    stock_map = {s.ticker: s for s in stocks}
    alerts: list[PriceAlert] = []

    for stk in stocks:
        # Ignore tickers that are new this cycle or not in our watch list
        if stk.previous_closed_price is None or stk.previous_closed_price == 0.0:
            # Avoid division by zero if a price was mistakenly stored as 0
            continue

        change_pct = ((stk.current_price - stk.previous_closed_price) / stk.previous_closed_price) * 100
        
        # Fire an alert only if the move exceeds the per-stock threshold
        if abs(change_pct) >= stk.alert_threshold_pct:
            alerts.append(
                PriceAlert(
                    ticker=stk.ticker,
                    name=stk.name,
                    current_price=stk.current_price,
                    previous_closed_price=stk.previous_closed_price,
                    change_pct=change_pct,
                )
            )

    return alerts
