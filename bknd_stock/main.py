import time
from datetime import datetime

from rich.console import Console

from bknd_stock.alerter import display_news, display_price_alert, display_price_table
from bknd_stock.config import load_config
from bknd_stock.monitor import detect_alerts, fetch_prices
from bknd_stock.news import fetch_news

console = Console()


def main() -> None:
    stocks, settings = load_config()
    poll_interval: int = settings["poll_interval_seconds"]
    news_interval: int = settings["news_fetch_interval_seconds"]

    console.print(
        f"\n[bold green]Stock Monitor started[/bold green]  "
        f"watching [cyan]{len(stocks)}[/cyan] stocks  "
        f"polling every [cyan]{poll_interval}s[/cyan]\n"
    )

    previous_prices: dict[str, float] = {}
    last_news_fetch: float = 0.0

    while True:
        try:
            now = time.time()
            timestamp = datetime.now().strftime("%H:%M:%S")

            current_prices = fetch_prices(stocks)
            display_price_table(stocks, current_prices, timestamp)

            if previous_prices:
                for alert in detect_alerts(stocks, previous_prices, current_prices):
                    display_price_alert(alert)

            previous_prices = current_prices

            if now - last_news_fetch >= news_interval:
                news = fetch_news(stocks)
                display_news(news)
                last_news_fetch = now

            time.sleep(poll_interval)

        except KeyboardInterrupt:
            console.print("\n[yellow]Monitor stopped.[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            time.sleep(poll_interval)


if __name__ == "__main__":
    main()
