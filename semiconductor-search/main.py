"""
Entry point for the Semiconductor Product Alternative Search API.

Run with:
    uvicorn main:app --host 0.0.0.0 --port $PORT --reload
"""

import sys
import os

# Allow imports from the project root when running from semiconductor-search/
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.db_client import initialize_schema
from api.routes import router

app = FastAPI(
    title="Semiconductor Product Alternative Search",
    description=(
        "Ingests locally-stored semiconductor HTML product pages, "
        "extracts specs, stores them in PostgreSQL, generates OpenAI embeddings, "
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

# Initialize the database schema on startup
@app.on_event("startup")
def on_startup():
    try:
        initialize_schema()
        print("[Startup] Database schema ready.")
    except Exception as e:
        print(f"[Startup] Warning: could not initialize schema: {e}")

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
