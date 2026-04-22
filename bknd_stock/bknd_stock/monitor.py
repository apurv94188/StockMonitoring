import yfinance as yf

from .models import PriceAlert, StockWatch


def fetch_prices(stocks: list[StockWatch]) -> dict[str, float]:
    tickers_str = " ".join(s.ticker for s in stocks)
    batch = yf.Tickers(tickers_str)
    prices: dict[str, float] = {}

    for stock in stocks:
        try:
            fast = batch.tickers[stock.ticker].fast_info
            price = fast.last_price or fast.previous_close
            if price is not None:
                prices[stock.ticker] = float(price)
        except Exception:
            pass

    return prices


def detect_alerts(
    stocks: list[StockWatch],
    previous: dict[str, float],
    current: dict[str, float],
) -> list[PriceAlert]:
    stock_map = {s.ticker: s for s in stocks}
    alerts: list[PriceAlert] = []

    for ticker, price in current.items():
        if ticker not in previous or ticker not in stock_map:
            continue

        prev = previous[ticker]
        if prev == 0:
            continue

        change_pct = ((price - prev) / prev) * 100
        stock = stock_map[ticker]

        if abs(change_pct) >= stock.alert_threshold_pct:
            alerts.append(
                PriceAlert(
                    ticker=ticker,
                    name=stock.name,
                    current_price=price,
                    previous_price=prev,
                    change_pct=change_pct,
                )
            )

    return alerts
