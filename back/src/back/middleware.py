"""HTTP request/response logging middleware.

This module provides :class:`RequestLoggingMiddleware`, a Starlette/FastAPI
middleware that:

* Generates a short unique **request ID** (8 hex chars) for every incoming
  request and stores it in :data:`back.context.request_id_var` so every log
  line emitted during that request carries the same ID.
* Logs the start of each request (method, path, client IP).
* Logs the outcome (HTTP status, duration in ms) after the response is sent.
* Catches and re-raises any unhandled exception so it is visible in the log
  before FastAPI's own exception machinery handles it.

The request ID is also returned to the caller via the ``X-Request-ID``
response header so that client-side developers can correlate their logs with
server-side logs.
"""

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.back.context import request_id_var

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs every HTTP request with timing and a unique ID.

    Attach to the FastAPI application with::

        app.add_middleware(RequestLoggingMiddleware)

    Log levels used:

    * ``INFO``  – normal request start and successful/redirect responses.
    * ``WARNING`` – 4xx client errors.
    * ``ERROR`` – 5xx server errors and unhandled exceptions.

    Context included in every log line (via :class:`back.logging_config.RequestContextFilter`):

    * ``request_id`` – 8-char hex token unique per request.
    * logger name (``back.middleware``).
    * timestamp and level (from the formatter in :mod:`back.logging_config`).

    Additional fields logged inline:

    * HTTP method and URL path.
    * Client IP address.
    * Response HTTP status code.
    * Round-trip duration in milliseconds.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process one request: log start, call handler, log outcome.

        Args:
            request: The incoming HTTP request.
            call_next: Callable that invokes the next middleware or route handler.

        Returns:
            Response: The HTTP response produced by the handler.

        Raises:
            Exception: Any exception raised by the handler is logged at ERROR
                level and then re-raised so FastAPI's exception handlers can
                produce the appropriate HTTP response.
        """
        # ── Assign request ID ──────────────────────────────────────────────
        request_id = uuid.uuid4().hex[:8]
        token = request_id_var.set(request_id)

        client_ip = request.client.host if request.client else "unknown"
        start = time.perf_counter()

        logger.info(
            "request started  method=%s path=%s client=%s",
            request.method,
            request.url.path,
            client_ip,
        )

        try:
            response: Response = await call_next(request)
        except Exception as exc:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.error(
                "request failed   method=%s path=%s client=%s duration=%.1fms error=%s",
                request.method,
                request.url.path,
                client_ip,
                duration_ms,
                repr(exc),
                exc_info=True,
            )
            raise
        finally:
            # Always reset the ContextVar so the token is not leaked.
            request_id_var.reset(token)

        duration_ms = (time.perf_counter() - start) * 1000

        # Choose log level based on HTTP status category.
        if response.status_code >= 500:
            log = logger.error
        elif response.status_code >= 400:
            log = logger.warning
        else:
            log = logger.info

        log(
            "request finished method=%s path=%s status=%d duration=%.1fms",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

        response.headers["X-Request-ID"] = request_id
        return response
