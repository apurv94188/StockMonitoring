import asyncio
import json
import time
from collections import deque
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .config import load_config
from .monitor import detect_alerts, fetch_prices
from .news import fetch_news

_state: dict = {
    "prices": {},
    "alerts": deque(maxlen=50),
    "news": [],
}
_subscribers: list[asyncio.Queue] = []


async def _broadcast(event_type: str, data) -> None:
    payload = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
    for q in list(_subscribers):
        await q.put(payload)


async def _monitor_loop() -> None:
    stocks, settings = load_config()
    poll_interval: int = settings["poll_interval_seconds"]
    news_interval: int = settings["news_fetch_interval_seconds"]
    previous_prices: dict[str, float] = {}
    last_news_fetch: float = 0.0
    loop = asyncio.get_event_loop()

    while True:
        now = time.time()

        current_prices: dict[str, float] = await loop.run_in_executor(
            None, fetch_prices, stocks
        )

        price_data = {
            ticker: {
                "ticker": ticker,
                "price": price,
                "name": next((s.name for s in stocks if s.ticker == ticker), ""),
                "change_pct": (
                    ((price - previous_prices[ticker]) / previous_prices[ticker] * 100)
                    if ticker in previous_prices and previous_prices[ticker]
                    else None
                ),
            }
            for ticker, price in current_prices.items()
        }
        _state["prices"] = price_data
        await _broadcast("prices", price_data)

        if previous_prices:
            for alert in detect_alerts(stocks, previous_prices, current_prices):
                alert_dict = {
                    "ticker": alert.ticker,
                    "name": alert.name,
                    "current_price": alert.current_price,
                    "previous_price": alert.previous_price,
                    "change_pct": alert.change_pct,
                    "timestamp": alert.timestamp.isoformat(),
                }
                _state["alerts"].appendleft(alert_dict)
                await _broadcast("alert", alert_dict)

        previous_prices = current_prices

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

        await asyncio.sleep(poll_interval)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(_monitor_loop())
    yield
    task.cancel()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/status")
def get_status():
    return {
        "prices": _state["prices"],
        "alerts": list(_state["alerts"]),
        "news": _state["news"],
    }


@app.get("/api/stream")
async def stream():
    q: asyncio.Queue = asyncio.Queue()
    _subscribers.append(q)

    async def generate():
        try:
            if _state["prices"]:
                yield f"event: prices\ndata: {json.dumps(_state['prices'])}\n\n"
            if _state["alerts"]:
                yield f"event: alerts\ndata: {json.dumps(list(_state['alerts']))}\n\n"
            if _state["news"]:
                yield f"event: news\ndata: {json.dumps(_state['news'])}\n\n"

            while True:
                payload = await q.get()
                yield payload
        finally:
            _subscribers.remove(q)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
