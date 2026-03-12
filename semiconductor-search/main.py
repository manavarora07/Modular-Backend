"""
Entry point for the Semiconductor Product Alternative Search API.

Run with:
    uvicorn main:app --host 0.0.0.0 --port $PORT --reload
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

app = FastAPI(
    title="Semiconductor Product Alternative Search",
    description=(
        "Ingests locally-stored semiconductor HTML product pages, "
        "extracts specs, stores them in Oracle Database, generates OpenAI embeddings, "
        "and finds alternative products using hybrid search."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Initialize Oracle DB schema on startup (skipped gracefully if credentials missing)."""
    try:
        from database.db_client import initialize_schema
        initialize_schema()
        print("[Startup] Oracle schema ready.")
    except RuntimeError as e:
        # Credentials not yet configured — app still starts, schema init deferred
        print(f"[Startup] Oracle not configured yet: {e}")
    except Exception as e:
        print(f"[Startup] Warning: could not initialize Oracle schema: {e}")


app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
