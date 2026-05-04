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


def detect_alerts(stocks: list[StockWatch], fired_alerts: set) -> list[PriceAlert]:
    # fired_alerts: set of (ticker, alert_type, threshold) owned by the caller.
    #
    # Three-zone hysteresis per threshold:
    #   fire zone   → condition met, not yet fired → fire + mark
    #   hold zone   → between threshold and reset line → stay marked, no re-fire
    #   reset zone  → retreated past (threshold ± buffer) → unmark, ready to fire again
    #
    # For pct_up  thr/buf:  fire: change_pct >= thr   reset: change_pct < thr - buf
    # For pct_down thr/buf: fire: change_pct <= -thr  reset: change_pct > -thr + buf
    # For price_above lvl/buf: fire: price >= lvl      reset: price < lvl - buf
    # For price_below lvl/buf: fire: price <= lvl      reset: price > lvl + buf
    alerts: list[PriceAlert] = []

    for stk in stocks:
        if stk.current_price is None or not stk.previous_closed_price:
            continue

        change_pct = ((stk.current_price - stk.previous_closed_price) / stk.previous_closed_price) * 100

        for pt in stk.alert_pct_thresholds:
            key_up = (stk.ticker, "pct_up", pt.threshold)
            if change_pct >= pt.threshold:
                if key_up not in fired_alerts:
                    fired_alerts.add(key_up)
                    alerts.append(PriceAlert(
                        ticker=stk.ticker, name=stk.name,
                        current_price=stk.current_price,
                        previous_closed_price=stk.previous_closed_price,
                        change_pct=change_pct, alert_type="pct_up", threshold=pt.threshold,
                    ))
            elif change_pct < pt.threshold - pt.buffer:
                fired_alerts.discard(key_up)

            key_down = (stk.ticker, "pct_down", pt.threshold)
            if change_pct <= -pt.threshold:
                if key_down not in fired_alerts:
                    fired_alerts.add(key_down)
                    alerts.append(PriceAlert(
                        ticker=stk.ticker, name=stk.name,
                        current_price=stk.current_price,
                        previous_closed_price=stk.previous_closed_price,
                        change_pct=change_pct, alert_type="pct_down", threshold=pt.threshold,
                    ))
            elif change_pct > -pt.threshold + pt.buffer:
                fired_alerts.discard(key_down)

        for pa in stk.alert_price_above:
            key = (stk.ticker, "price_above", pa.level)
            if stk.current_price >= pa.level:
                if key not in fired_alerts:
                    fired_alerts.add(key)
                    alerts.append(PriceAlert(
                        ticker=stk.ticker, name=stk.name,
                        current_price=stk.current_price,
                        previous_closed_price=stk.previous_closed_price,
                        change_pct=change_pct, alert_type="price_above", threshold=pa.level,
                    ))
            elif stk.current_price < pa.level - pa.buffer:
                fired_alerts.discard(key)

        for pb in stk.alert_price_below:
            key = (stk.ticker, "price_below", pb.level)
            if stk.current_price <= pb.level:
                if key not in fired_alerts:
                    fired_alerts.add(key)
                    alerts.append(PriceAlert(
                        ticker=stk.ticker, name=stk.name,
                        current_price=stk.current_price,
                        previous_closed_price=stk.previous_closed_price,
                        change_pct=change_pct, alert_type="price_below", threshold=pb.level,
                    ))
            elif stk.current_price > pb.level + pb.buffer:
                fired_alerts.discard(key)

    return alerts
