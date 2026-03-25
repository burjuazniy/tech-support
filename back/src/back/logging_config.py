"""Logging configuration for the Tech Support backend.

This module exposes a single public function :func:`configure_logging` that
must be called **once**, before the FastAPI application is imported, so that
every logger in the process inherits the correct handlers and formatters.

Architecture
------------
Three handlers are registered on the root logger:

1. **Console** (``StreamHandler``) – always active, level controlled by the
   caller (``LOG_LEVEL`` env-var / ``--log-level`` CLI flag).
2. **App file** (``TimedRotatingFileHandler``) – rotates at midnight, keeps
   30 days of history; records INFO and above.
3. **Error file** (``RotatingFileHandler``) – rotates at 5 MB, keeps the
   5 most recent files; records ERROR and above only.

Log format
----------
Every record carries::

    2026-03-25 14:01:02 | INFO     | back.main          | a1b2c3d4 | message

Fields: timestamp · level (8 chars padded) · logger name · request ID · message.
The ``request_id`` field is injected by :class:`RequestContextFilter` from the
:data:`back.context.request_id_var` ContextVar; outside a request it shows ``-``.

Configuring the log level without recompiling
---------------------------------------------
Python's :mod:`logging` module does not require recompilation to change the
minimum log level.  In this project the level is resolved in the following
priority order (highest first):

1. ``--log-level`` CLI flag passed to ``run.py`` (e.g. ``python run.py
   --log-level WARNING``).
2. ``LOG_LEVEL`` environment variable (e.g. ``LOG_LEVEL=WARNING python
   run.py``).
3. Compiled-in default: ``DEBUG``.

This is a standard feature of Python's logging infrastructure – the level is
just an integer stored on a :class:`logging.Logger` object and can be changed
at any point with :meth:`logging.Logger.setLevel`.

Log rotation
------------
- **By time** (``TimedRotatingFileHandler``): a new ``logs/app.log`` file is
  started at midnight every day.  Old files are renamed to
  ``logs/app.log.YYYY-MM-DD``.  Files older than 30 days are deleted
  automatically by the handler.
- **By size** (``RotatingFileHandler``): ``logs/errors.log`` is capped at
  5 MB.  When the cap is reached the handler renames the current file to
  ``errors.log.1`` (shifting older backups up to ``.5``) and opens a fresh
  file.  At most 5 backup files are kept, so the total error log footprint
  stays below ~30 MB.

Both handlers are part of the Python standard library – no extra packages are
required.
"""

import logging
import logging.handlers
from pathlib import Path

from src.back.context import request_id_var

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LOG_DIR = Path("logs")
_FMT = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(request_id)s | %(message)s"
_DATE_FMT = "%Y-%m-%d %H:%M:%S"

_APP_LOG = LOG_DIR / "app.log"
_ERR_LOG = LOG_DIR / "errors.log"

_APP_ROTATE_DAYS = 30       # keep 30 daily files
_ERR_MAX_BYTES = 5 * 1024 * 1024  # 5 MB per file
_ERR_BACKUP_COUNT = 5       # keep 5 error-log backups


# ---------------------------------------------------------------------------
# Filter – injects request_id into every LogRecord
# ---------------------------------------------------------------------------

class RequestContextFilter(logging.Filter):
    """Attach the current ``request_id`` to every :class:`logging.LogRecord`.

    This filter reads :data:`back.context.request_id_var` (a ``ContextVar``)
    and writes its value into ``record.request_id``.  Because ``ContextVar``
    values are isolated per async task, concurrent requests never bleed into
    each other's log lines.

    The filter is added to **all** handlers so the field is available
    regardless of which handler emits the record.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """Inject ``request_id`` and return ``True`` to allow the record.

        Args:
            record: The log record being processed.

        Returns:
            bool: Always ``True`` – this filter never drops records.
        """
        record.request_id = request_id_var.get("-")
        return True


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def configure_logging(log_level: str = "DEBUG") -> None:
    """Set up all logging handlers for the application process.

    Call this function **exactly once**, before importing
    :mod:`back.main`, so the handlers are in place when the FastAPI
    application initialises.

    Args:
        log_level: Minimum severity to emit on the **console** handler.
            Accepts any value accepted by :func:`logging.getLevelName`
            (case-insensitive): ``"DEBUG"``, ``"INFO"``, ``"WARNING"``,
            ``"ERROR"``, ``"CRITICAL"``.  The file handlers always capture
            ``INFO`` and above (app log) or ``ERROR`` and above (error log),
            regardless of this parameter.

    Side effects:
        - Creates the ``logs/`` directory if it does not already exist.
        - Configures the root :class:`logging.Logger` (level ``DEBUG``).
        - Adds three :class:`logging.Handler` instances to the root logger.
        - Suppresses overly chatty third-party loggers (``uvicorn.access``).

    Example:
        >>> configure_logging("WARNING")  # silence DEBUG/INFO on console
    """
    LOG_DIR.mkdir(exist_ok=True)

    numeric_level = logging.getLevelName(log_level.upper())
    if not isinstance(numeric_level, int):
        numeric_level = logging.DEBUG

    formatter = logging.Formatter(_FMT, datefmt=_DATE_FMT)
    context_filter = RequestContextFilter()

    # ── 1. Console handler ──────────────────────────────────────────────────
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(context_filter)

    # ── 2. App file – rotates daily, keeps 30 days ──────────────────────────
    # TimedRotatingFileHandler is part of the Python stdlib (logging.handlers).
    # At midnight (when="midnight") the handler closes the current file,
    # renames it to app.log.YYYY-MM-DD, then opens a fresh app.log.
    # Files older than backupCount=30 days are deleted automatically.
    app_file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=_APP_LOG,
        when="midnight",
        backupCount=_APP_ROTATE_DAYS,
        encoding="utf-8",
    )
    app_file_handler.setLevel(logging.INFO)
    app_file_handler.setFormatter(formatter)
    app_file_handler.addFilter(context_filter)

    # ── 3. Error file – rotates at 5 MB, keeps 5 backups ───────────────────
    # RotatingFileHandler is also part of the Python stdlib.
    # When the current file exceeds maxBytes the handler renames it to
    # errors.log.1, shifting older files to .2 ... .5.  The oldest backup
    # (.5) is deleted when a new rotation is needed.
    err_file_handler = logging.handlers.RotatingFileHandler(
        filename=_ERR_LOG,
        maxBytes=_ERR_MAX_BYTES,
        backupCount=_ERR_BACKUP_COUNT,
        encoding="utf-8",
    )
    err_file_handler.setLevel(logging.ERROR)
    err_file_handler.setFormatter(formatter)
    err_file_handler.addFilter(context_filter)

    # ── Root logger ─────────────────────────────────────────────────────────
    # Set root to DEBUG so handlers can independently decide what they emit.
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(app_file_handler)
    root_logger.addHandler(err_file_handler)

    # ── Suppress noisy third-party loggers ──────────────────────────────────
    # uvicorn.access logs every HTTP request at INFO level in its own format.
    # We handle request logging ourselves in RequestLoggingMiddleware, so we
    # silence this to avoid duplicate lines.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
