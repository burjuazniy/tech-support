"""Main application module for the Tech Support backend.

This module initialises the FastAPI application, registers middleware,
declares global exception handlers, and defines the top-level HTTP routes.

Standards: Google-style docstrings (PEP 257 + Google style guide).
Auto-docs: FastAPI exposes built-in OpenAPI UI at ``/docs`` (Swagger) and
``/redoc`` (ReDoc). Sphinx with ``sphinx.ext.autodoc`` is used for offline
HTML documentation – see ``docs/generate_docs.md``.

Error handling strategy
-----------------------
* Every unhandled exception is caught by :func:`global_exception_handler`.
* A unique ``error_id`` (UUID4) is generated per exception so a specific
  incident can be located in the log files by searching for that ID.
* The ``error_id`` is returned to the client in the JSON response so the user
  or support team can reference it when filing a bug report.
* Full stack traces are written to the log at ERROR level.
* Contextual information (request method, path, client IP, request ID) is
  available on every log line via :class:`back.middleware.RequestLoggingMiddleware`
  and :class:`back.logging_config.RequestContextFilter`.
"""

import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.back.middleware import RequestLoggingMiddleware

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan (startup / shutdown)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Manage application startup and shutdown lifecycle.

    FastAPI recommends using an ``asynccontextmanager`` lifespan instead of the
    deprecated ``@app.on_event`` decorators.  Code before ``yield`` runs on
    startup; code after ``yield`` runs on shutdown.

    Args:
        app: The FastAPI application instance (injected by the framework).

    Yields:
        None: Control is yielded to the request-handling loop.
    """
    logger.info("application startup complete – ready to accept requests")
    yield
    logger.info("application shutdown initiated – stopping gracefully")


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Tech Support API",
    description="REST backend for the Tech Support application.",
    version="0.1.0",
    lifespan=lifespan,
)
"""FastAPI application instance.

All routes, middleware, and exception handlers are registered on this object.
"""

# ── Middleware (order matters – first registered = outermost wrapper) ────────

# RequestLoggingMiddleware must wrap CORSMiddleware so every request gets an
# ID before CORS headers are processed.
app.add_middleware(RequestLoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Global exception handlers
# ---------------------------------------------------------------------------


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch any unhandled exception and return a structured JSON error response.

    This handler is the last line of defence.  It ensures that:

    * The exception is **always** logged at ``ERROR`` level with a full
      stack trace (``exc_info=True``).
    * A unique ``error_id`` is generated so the incident can be found in the
      log files by searching for that exact UUID.
    * The client receives a safe, generic message instead of a raw Python
      traceback (which would leak implementation details).
    * Contextual information (method, path, client IP) is included in the log
      line so the engineer does not need to cross-reference other log files.

    Args:
        request: The HTTP request that triggered the exception.
        exc: The unhandled exception.

    Returns:
        JSONResponse: HTTP 500 response with ``error_id`` and ``detail`` keys.

    Example response body::

        {
            "error_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
            "detail": "Internal server error. Quote error_id when reporting."
        }
    """
    error_id = str(uuid.uuid4())
    client_ip = request.client.host if request.client else "unknown"

    logger.error(
        "unhandled exception  error_id=%s method=%s path=%s client=%s exc_type=%s",
        error_id,
        request.method,
        request.url.path,
        client_ip,
        type(exc).__name__,
        exc_info=True,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error_id": error_id,
            "detail": "Internal server error. Quote error_id when reporting.",
        },
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/", summary="Health check", tags=["general"])
async def root() -> dict[str, str]:
    """Return a simple greeting to verify the API is running.

    This endpoint serves as a lightweight health-check and entry point for the
    API. No authentication is required.

    Returns:
        dict[str, str]: A JSON object with a single ``message`` key, e.g.
            ``{"message": "Hello World"}``.

    Example:
        >>> import httpx
        >>> response = httpx.get("http://localhost:8000/")
        >>> response.json()
        {'message': 'Hello World'}
    """
    logger.debug("health-check endpoint called")
    return {"message": "Hello World"}
