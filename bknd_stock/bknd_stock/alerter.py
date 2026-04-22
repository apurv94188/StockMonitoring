import subprocess

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .models import NewsItem, PriceAlert, StockWatch

console = Console()


def display_price_table(stocks: list[StockWatch], prices: dict[str, float], timestamp: str) -> None:
    table = Table(title=f"Stock Prices  {timestamp}", show_lines=False, expand=False)
    table.add_column("Ticker", style="bold cyan", width=8)
    table.add_column("Name", style="dim")
    table.add_column("Price", justify="right", style="white")

    stock_map = {s.ticker: s for s in stocks}
    for ticker, price in prices.items():
        name = stock_map[ticker].name if ticker in stock_map else ""
        table.add_row(ticker, name, f"${price:,.2f}")

    console.print(table)


def display_price_alert(alert: PriceAlert) -> None:
    up = alert.change_pct > 0
    arrow = "▲" if up else "▼"
    color = "green" if up else "red"
    sign = "+" if up else ""

    text = Text()
    text.append(f"  {arrow} {alert.ticker}", style=f"bold {color}")
    text.append(f"  {sign}{alert.change_pct:.2f}%", style=f"bold {color}")
    text.append(f"  ${alert.current_price:,.2f}", style="white")
    text.append(f"  (was ${alert.previous_price:,.2f})", style="dim")
    text.append(f"\n  {alert.name}", style="dim")

    console.print(Panel(text, title="[bold yellow]Price Alert[/bold yellow]", border_style=color))

    _macos_notify(
        title=f"{alert.ticker} {arrow} {sign}{alert.change_pct:.1f}%",
        message=f"{alert.name}: ${alert.current_price:,.2f}",
    )


def display_news(items: list[NewsItem]) -> None:
    if not items:
        return

    console.rule("[bold blue]Recent News[/bold blue]")
    for item in items:
        ticker_tag = f"[bold cyan][{item.ticker}][/bold cyan] " if item.ticker else ""
        source = f"[dim italic]— {item.source}[/dim italic]"
        console.print(f"  {ticker_tag}[link={item.link}]{item.title}[/link] {source}")
    console.print()


def _macos_notify(title: str, message: str) -> None:
    script = f'display notification "{message}" with title "{title}"'
    try:
        subprocess.run(["osascript", "-e", script], check=False, capture_output=True)
    except FileNotFoundError:
        pass
