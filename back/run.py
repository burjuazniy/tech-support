"""Development entry-point for the Tech Support backend.

Run this script directly to start a local Uvicorn server::

    python run.py

The server listens on ``http://127.0.0.1:8000`` by default.
Hot-reload is enabled when ``DEBUG = True``.

Configuring the log level
--------------------------
The minimum log level for the **console** handler can be changed without
touching the source code or restarting with a different binary.  Resolution
order (highest priority first):

1. ``--log-level`` CLI flag::

       python run.py --log-level WARNING

2. ``LOG_LEVEL`` environment variable::

       LOG_LEVEL=WARNING python run.py
       # or in PowerShell:
       $env:LOG_LEVEL="WARNING"; python run.py

3. Compiled-in default: ``DEBUG``.

Accepted values (case-insensitive): ``DEBUG``, ``INFO``, ``WARNING``,
``ERROR``, ``CRITICAL``.

This approach is a standard feature of Python's :mod:`logging` module – the
level is simply an integer attribute on a :class:`logging.Logger` instance and
can be changed at any time via :meth:`~logging.Logger.setLevel` without any
compilation or process restart.  We expose it as an env-var / CLI flag so
operators can tune verbosity in different environments (local dev vs CI vs
staging) without modifying code.
"""

import argparse
import os

# ---------------------------------------------------------------------------
# Resolve log level before importing application code so every logger that
# is instantiated at import time already inherits the correct level.
# ---------------------------------------------------------------------------

def _resolve_log_level() -> str:
    """Return the log level string from CLI flag, env-var, or default.

    Returns:
        str: Uppercase log level name, e.g. ``"DEBUG"``.
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--log-level",
        default=None,
        metavar="LEVEL",
        help="Minimum log level for console output (DEBUG/INFO/WARNING/ERROR/CRITICAL).",
    )
    # parse_known_args so uvicorn's own argv is not rejected.
    args, _ = parser.parse_known_args()

    if args.log_level:
        return args.log_level.upper()
    return os.environ.get("LOG_LEVEL", "DEBUG").upper()


_LOG_LEVEL = _resolve_log_level()

# Configure logging FIRST – before any application module is imported.
from src.back.logging_config import configure_logging  # noqa: E402
configure_logging(_LOG_LEVEL)

# Now it is safe to import the application.
import logging  # noqa: E402
import uvicorn  # noqa: E402

logger = logging.getLogger(__name__)

DEBUG = True
"""bool: When ``True`` the Uvicorn server starts with hot-reload enabled.
Set to ``False`` for a production-like local run (no file watching)."""

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logger.info("starting server host=127.0.0.1 port=8000 debug=%s log_level=%s", DEBUG, _LOG_LEVEL)
    uvicorn.run(
        "src.back.main:app",
        host="127.0.0.1",
        port=8000,
        reload=DEBUG,
        # Disable uvicorn's own log config – we manage it via logging_config.
        log_config=None,
    )
    logger.info("server process exited")
