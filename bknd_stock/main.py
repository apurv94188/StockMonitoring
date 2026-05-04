# CLI entry point — run this directly to monitor stocks in the terminal (no web server).
# Uses Rich for colored console output. For the web dashboard, use serve.py instead.

import time
from datetime import datetime

from rich.console import Console

from bknd_stock.alerter import display_news, display_price_alert, display_price_table, send_pushover_alert
from bknd_stock.config import load_config, load_pushover_keys
from bknd_stock.monitor import detect_alerts, fetch_prices
from bknd_stock.news import fetch_news

console = Console()


def main() -> None:
    stocks, settings, api_key = load_config()
    pushover_token, pushover_user_key = load_pushover_keys()
    fired_alerts: set = set()  # (ticker, alert_type, threshold) — persists across poll cycles
    poll_interval: int = settings["poll_interval_seconds"]
    news_interval: int = settings["news_fetch_interval_seconds"]

    console.print(
        f"\n[bold green]Stock Monitor started[/bold green]  "
        f"watching [cyan]{len(stocks)}[/cyan] stocks  "
        f"polling every [cyan]{poll_interval}s[/cyan]\n"
    )

    last_news_fetch: float = 0.0

    while True:
        try:
            now = time.time()
            timestamp = datetime.now().strftime("%H:%M:%S")

            stocks = fetch_prices(stocks, api_key)
            display_price_table(stocks, timestamp)

            for alert in detect_alerts(stocks, fired_alerts):
                display_price_alert(alert)
                if pushover_token and pushover_user_key:
                    send_pushover_alert(alert, pushover_token, pushover_user_key)

            if now - last_news_fetch >= news_interval:
                news = fetch_news(stocks)
                display_news(news)
                last_news_fetch = now

            time.sleep(poll_interval)

        except KeyboardInterrupt:
            console.print("\n[yellow]Monitor stopped.[/yellow]")
            break
        except Exception as e:
            # Keep running after transient errors (network blip, bad ticker, etc.)
            console.print(f"[red]Error: {e}[/red]")
            time.sleep(poll_interval)


if __name__ == "__main__":
    main()
