# FastAPI web server — serves the SSE stream and a one-shot status endpoint.
# The frontend connects to /api/stream and receives real-time price, alert, and news events.
# Run via serve.py (uvicorn wrapper).

import asyncio
import json
import time
from collections import deque
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .alerter import send_pushover_alert
from .config import load_config, load_pushover_keys
from .monitor import detect_alerts, fetch_prices
from .news import fetch_news
from .models import StockWatch

# --- Shared in-memory state ---
# _state is a single dict shared across all requests in the same process.
# "prices" is keyed by ticker and holds the latest price payload for each stock.
# "alerts" is a deque (FIFO, max 50) so old alerts are automatically dropped.
# "news" is the full list from the last news fetch cycle.
_state: dict = {
    "prices": {},
    "alerts": deque(maxlen=50),
    "news": [],
}

# Each connected SSE client has its own asyncio.Queue in this list.
# _broadcast() puts events onto every queue; each generate() coroutine drains its own queue.
_subscribers: list[asyncio.Queue] = []


async def _broadcast(event_type: str, data) -> None:
    # Format follows the SSE spec: "event: <type>\ndata: <json>\n\n"
    payload = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
    for q in list(_subscribers):  # list() copy prevents issues if a subscriber disconnects mid-loop
        await q.put(payload)


async def _monitor_loop() -> None:
    # Background task that runs for the lifetime of the server.
    # Fetches prices on every poll cycle and news on a slower interval.
    stocks, settings, api_key = load_config()
    pushover_token, pushover_user_key = load_pushover_keys()
    fired_alerts: set = set()  # (ticker, alert_type, threshold) — persists across poll cycles
    poll_interval: int = settings["poll_interval_seconds"]
    news_interval: int = settings["news_fetch_interval_seconds"]
    last_news_fetch: float = 0.0
    loop = asyncio.get_event_loop()

    while True:
        try:
            now = time.time()

            stocks: list[StockWatch] = await loop.run_in_executor(
                None, fetch_prices, stocks, api_key
            )

            # Build the full price payload including name and % change for each ticker
            price_data = {
                stk.ticker: {
                    "ticker": stk.ticker,
                    "price": stk.current_price,
                    "name": stk.name, # next((s.name for s in stocks if s.ticker == ticker), ""),
                    # change_pct is None on the very first poll (no previous_prices yet)
                    "change_pct": (
                        ((stk.current_price - stk.previous_closed_price) / stk.previous_closed_price * 100)
                        if stk.current_price and stk.previous_closed_price
                        else None
                    ),
                    "current_price_timestamp": stk.current_price_timestamp.isoformat() if stk.current_price_timestamp else None
                }
                for stk in stocks
            }
            _state["prices"] = price_data
            await _broadcast("prices", price_data)

            # Detect threshold breaches and push individual "alert" events
            for alert in detect_alerts(stocks, fired_alerts):
                if pushover_token and pushover_user_key:
                    loop.run_in_executor(None, send_pushover_alert, alert, pushover_token, pushover_user_key)
                alert_dict = {
                    "ticker": alert.ticker,
                    "name": alert.name,
                    "current_price": alert.current_price,
                    "previous_price": alert.previous_closed_price,
                    "change_pct": alert.change_pct,
                    "alert_type": alert.alert_type,
                    "threshold": alert.threshold,
                    "timestamp": alert.timestamp.isoformat(),
                }
                # appendleft keeps the deque sorted newest-first
                _state["alerts"].appendleft(alert_dict)
                await _broadcast("alert", alert_dict)

            # News fetch only when the interval has elapsed (default: every 5 minutes)
            if now - last_news_fetch >= news_interval:
                news = await loop.run_in_executor(None, fetch_news, stocks)
                news_data = [
                    {
                        "title": item.title,
                        "link": item.link,
                        "published": item.published,
                        "source": item.source,
                        "ticker": item.ticker,
                    }
                    for item in news
                ]
                _state["news"] = news_data
                await _broadcast("news", news_data)
                last_news_fetch = now

        except Exception as e:
            print(f"[monitor loop error] {e}")

        await asyncio.sleep(poll_interval)


#### lifespan (below code) #####
# in general case
# yield returns a value without ending the function
# The function pauses
# Next time it's called, it continues from where it left off
# but here in FastAPI yield acts differently
# Here, yield is not returning data — it's acting as a split point.
# BEFORE yield  → startup code
# AT yield      → app runs
# AFTER yield   → shutdown code

# This function will run:
# once at startup
# once at shutdown
@asynccontextmanager    # This comes from Python’s async utilities. It allows you to write a function that has: # setup code (before yield) and teardown code (after yield)
async def lifespan(app: FastAPI):
    # Start the _monitor_loop() function above in async mode. Since, the next line is yield so this lifespan function pauses and when the \
    # _monitor_loop() ends then this lifespan resumes. After resuming it hits task.cancel() which cancels the async job
    task = asyncio.create_task(_monitor_loop())
    yield   # Pauses here and lets FastAPI run normally
    task.cancel()   # When server shuts down → resumes after yield

# In FastAPI, a lifespan function lets you define:
# startup behavior (before the server begins handling requests)
# shutdown behavior (when the server is stopping)
app = FastAPI(lifespan=lifespan)

# Allow the Vite dev server (any origin) to connect during development.
# In production, restrict allow_origins to your actual frontend domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/status")
def get_status():
    # One-shot snapshot of current state — useful for debugging without opening an SSE stream
    return {
        "prices": _state["prices"],
        "alerts": list(_state["alerts"]),
        "news": _state["news"],
    }


@app.get("/api/stream")
async def stream():
    # Server-Sent Events endpoint — the frontend keeps this connection open indefinitely.
    # Each client gets its own Queue; _broadcast() pushes into all queues simultaneously.
    q: asyncio.Queue = asyncio.Queue()
    _subscribers.append(q)

    async def generate():
        try:
            # Immediately send whatever state is already known so the UI isn't blank
            # while waiting for the next poll cycle to fire
            if _state["prices"]:
                yield f"event: prices\ndata: {json.dumps(_state['prices'])}\n\n"
            if _state["alerts"]:
                yield f"event: alerts\ndata: {json.dumps(list(_state['alerts']))}\n\n"
            if _state["news"]:
                yield f"event: news\ndata: {json.dumps(_state['news'])}\n\n"

            # Block until the next broadcast arrives, then forward it to this client
            while True:
                payload = await q.get()
                yield payload
        finally:
            # Remove the queue when the client disconnects to prevent memory leak
            _subscribers.remove(q)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        # Cache-Control: no-cache is required by the SSE spec
        # X-Accel-Buffering: no tells nginx not to buffer the stream
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
