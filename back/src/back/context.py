"""Per-request context storage using Python contextvars.

Each incoming HTTP request gets a unique ``request_id`` injected by
:mod:`back.middleware`.  The value is stored in a ``ContextVar`` so it is
automatically isolated between concurrent async tasks – no thread-local
tricks needed.

The logging filter in :mod:`back.logging_config` reads from this module to
attach the request ID to every log record produced during a request's
lifetime, even across ``await`` boundaries.
"""

from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")
"""ContextVar[str]: Stores the short request ID for the current async context.

Set by :class:`back.middleware.RequestLoggingMiddleware` at the beginning of
each request and cleared automatically when the request coroutine exits.
Defaults to ``"-"`` outside of a request context (e.g. during startup).
"""
