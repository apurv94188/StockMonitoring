# Web server entry point — starts the FastAPI app defined in bknd_stock/api.py.
# Run with:  python serve.py
# The frontend Vite dev server proxies /api/* to this on port 8000.

import uvicorn

if __name__ == "__main__":
    # reload=False keeps a single process so the shared _state dict in api.py stays intact.
    # With reload=True, each reload spins a new worker that loses in-memory state.
    uvicorn.run("bknd_stock.api:app", host="0.0.0.0", port=8000, reload=False)
