# Terminal display functions — used only by main.py (the CLI mode).
# The web server (api.py) sends data as JSON over SSE instead of printing here.
# send_pushover_alert is shared by both modes.

import subprocess
import urllib.parse
import urllib.request

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .models import NewsItem, PriceAlert, StockWatch

console = Console()


def display_price_table(stocks: list[StockWatch], timestamp: str) -> None:
    table = Table(title=f"Stock Prices  {timestamp}", show_lines=False, expand=False)
    table.add_column("Ticker", style="bold cyan", width=8)
    table.add_column("Name", style="dim")
    table.add_column("Price", justify="right", style="white")

    for stk in stocks:
        price = f"${stk.current_price:,.2f}" if stk.current_price is not None else "—"
        table.add_row(stk.ticker, stk.name, price)

    console.print(table)


def display_price_alert(alert: PriceAlert) -> None:
    up = alert.alert_type in ("pct_up", "price_above")
    color = "green" if up else "red"
    arrow = "▲" if up else "▼"

    text = Text()
    if alert.alert_type == "pct_up":
        text.append(f"  {arrow} {alert.ticker}", style=f"bold {color}")
        text.append(f"  +{alert.change_pct:.2f}%", style=f"bold {color}")
        text.append(f"  (≥+{alert.threshold:.1f}%)", style="dim")
        text.append(f"  ${alert.current_price:,.2f}", style="white")
        text.append(f"  prev ${alert.previous_closed_price:,.2f}", style="dim")
        notify_title = f"{alert.ticker} {arrow} +{alert.change_pct:.1f}%"
    elif alert.alert_type == "pct_down":
        text.append(f"  {arrow} {alert.ticker}", style=f"bold {color}")
        text.append(f"  {alert.change_pct:.2f}%", style=f"bold {color}")
        text.append(f"  (≤-{alert.threshold:.1f}%)", style="dim")
        text.append(f"  ${alert.current_price:,.2f}", style="white")
        text.append(f"  prev ${alert.previous_closed_price:,.2f}", style="dim")
        notify_title = f"{alert.ticker} {arrow} {alert.change_pct:.1f}%"
    elif alert.alert_type == "price_above":
        text.append(f"  {arrow} {alert.ticker}", style=f"bold {color}")
        text.append(f"  crossed above ${alert.threshold:,.2f}", style=f"bold {color}")
        text.append(f"  now ${alert.current_price:,.2f}", style="white")
        notify_title = f"{alert.ticker} above ${alert.threshold:,.2f}"
    else:  # price_below
        text.append(f"  {arrow} {alert.ticker}", style=f"bold {color}")
        text.append(f"  crossed below ${alert.threshold:,.2f}", style=f"bold {color}")
        text.append(f"  now ${alert.current_price:,.2f}", style="white")
        notify_title = f"{alert.ticker} below ${alert.threshold:,.2f}"

    text.append(f"\n  {alert.name}", style="dim")
    console.print(Panel(text, title="[bold yellow]Price Alert[/bold yellow]", border_style=color))
    _macos_notify(title=notify_title, message=f"{alert.name}: ${alert.current_price:,.2f}")


def display_news(items: list[NewsItem]) -> None:
    if not items:
        return

    console.rule("[bold blue]Recent News[/bold blue]")
    for item in items:
        # Prefix with ticker badge when available
        ticker_tag = f"[bold cyan][{item.ticker}][/bold cyan] " if item.ticker else ""
        source = f"[dim italic]— {item.source}[/dim italic]"
        console.print(f"  {ticker_tag}[link={item.link}]{item.title}[/link] {source}")
    console.print()


def send_pushover_alert(alert: PriceAlert, token: str, user_key: str) -> None:
    if alert.alert_type == "pct_up":
        title = f"▲ {alert.ticker} +{alert.change_pct:.1f}% (≥+{alert.threshold:.1f}%)"
        message = f"{alert.name}: ${alert.current_price:,.2f} (was ${alert.previous_closed_price:,.2f})"
    elif alert.alert_type == "pct_down":
        title = f"▼ {alert.ticker} {alert.change_pct:.1f}% (≤-{alert.threshold:.1f}%)"
        message = f"{alert.name}: ${alert.current_price:,.2f} (was ${alert.previous_closed_price:,.2f})"
    elif alert.alert_type == "price_above":
        title = f"▲ {alert.ticker} crossed above ${alert.threshold:,.2f}"
        message = f"{alert.name} now at ${alert.current_price:,.2f}"
    else:  # price_below
        title = f"▼ {alert.ticker} crossed below ${alert.threshold:,.2f}"
        message = f"{alert.name} now at ${alert.current_price:,.2f}"

    data = urllib.parse.urlencode({
        "token": token,
        "user": user_key,
        "title": title,
        "message": message,
    }).encode()
    try:
        req = urllib.request.Request(
            "https://api.pushover.net/1/messages.json",
            data=data,
            method="POST",
        )
        urllib.request.urlopen(req, timeout=10).close()
    except Exception as e:
        print(f"[pushover] {e}")


def _macos_notify(title: str, message: str) -> None:
    # Uses AppleScript to send a macOS system notification — silently skipped on non-Mac
    script = f'display notification "{message}" with title "{title}"'
    try:
        subprocess.run(["osascript", "-e", script], check=False, capture_output=True)
    except FileNotFoundError:
        # osascript not available (Linux/Windows) — just skip the notification
        pass
