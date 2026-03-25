"""Development entry-point for the Tech Support backend.

Run this script directly to start a local Uvicorn server::

    python run.py

The server listens on ``http://127.0.0.1:8000`` by default.
Hot-reload is enabled when ``DEBUG = True``.
"""

import logging

DEBUG = True
"""bool: When ``True`` the server starts in debug mode with auto-reload and
verbose logging. Set to ``False`` for production-like local runs."""

logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

import uvicorn


if __name__ == "__main__":
    uvicorn.run("src.back.main:app", host="127.0.0.1", port=8000, reload=DEBUG)
