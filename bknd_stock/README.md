# bknd-stock

Stock price monitor with news feed alerts. Polls Yahoo Finance for live prices, detects threshold-based alerts, and exposes a FastAPI backend with Server-Sent Events for real-time frontend consumption.

## Prerequisites

- **Python 3.12+**
- **[uv](https://docs.astral.sh/uv/)** (recommended) — or `pip`

Install `uv` if you don't have it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Install Dependencies

```bash
uv sync
```

Or with pip in a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install .
```

## Configuration

Edit [stocks.json](stocks.json) to set which stocks to watch and polling intervals:

```json
{
  "stocks": [
    { "ticker": "AAPL", "name": "Apple Inc.", "alert_threshold_pct": 0.5 }
  ],
  "settings": {
    "poll_interval_seconds": 30,
    "news_fetch_interval_seconds": 300
  }
}
```

`alert_threshold_pct` is the minimum percentage price change that triggers an alert.

## Running

### API server (for frontend)

```bash
uv run python serve.py
```

The server starts on `http://localhost:8000`.

| Endpoint | Description |
|---|---|
| `GET /api/status` | Current prices, recent alerts, and latest news |
| `GET /api/stream` | Server-Sent Events stream (`prices`, `alert`, `news` events) |

### CLI monitor (terminal only)

```bash
uv run python main.py
```

Displays a live price table and prints alerts/news directly to the terminal. Stop with `Ctrl+C`.
