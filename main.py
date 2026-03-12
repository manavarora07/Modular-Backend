"""Workspace entrypoint for the Oracle-backed semiconductor search API.

This keeps a single Python runtime path and forwards to
`semiconductor-search/main.py`.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SEMICONDUCTOR_MAIN = PROJECT_ROOT / "semiconductor-search" / "main.py"


def _load_app_module():
    spec = importlib.util.spec_from_file_location("semiconductor_search_main", SEMICONDUCTOR_MAIN)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load FastAPI app module: {SEMICONDUCTOR_MAIN}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


module = _load_app_module()
app = module.app


def main() -> None:
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)


if __name__ == "__main__":
    main()
