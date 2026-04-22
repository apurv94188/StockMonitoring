# frtnd-stock

Real-time stock monitor dashboard built with React + Vite. Streams live prices, threshold alerts, and news from the `bknd-stock` backend via Server-Sent Events.

## Prerequisites

- **Node.js 18+** and **npm**
- The [bknd-stock](../bknd_stock) backend running on `http://localhost:8000`

## Install Dependencies

```bash
npm install
```

## Running

### Development server

```bash
npm run dev
```

Opens at `http://localhost:5173`. API requests to `/api/*` are proxied to the backend at `http://127.0.0.1:8000` — start the backend first.

### Production build

```bash
npm run build
```

Output is written to `dist/`. Serve it with any static file host.

### Preview production build locally

```bash
npm run preview
```

## Features

- **Price grid** — live stock price cards updated in real time, with directional arrows for price movement
- **Alert feed** — price threshold alerts (last 30) showing ticker, % change, and price range
- **News feed** — relevant news articles per stock, refreshed every 5 minutes
- **Connection status** — header indicator shows whether the SSE stream is live

## Architecture

The app connects to the backend's `/api/stream` endpoint using the EventSource API and listens for three event types:

| Event | Description |
|---|---|
| `prices` | Current prices for all tracked stocks |
| `alert` / `alerts` | Individual alert or initial batch on connect |
| `news` | Latest news articles |

No environment variables are required — the Vite dev proxy handles backend routing automatically.
