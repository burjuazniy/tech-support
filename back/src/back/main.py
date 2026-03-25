"""Main application module for the Tech Support backend.

This module initialises the FastAPI application, registers CORS middleware,
and declares the top-level HTTP routes.

Standards: Google-style docstrings (PEP 257 + Google style guide).
Auto-docs: FastAPI exposes built-in OpenAPI UI at ``/docs`` (Swagger) and
``/redoc`` (ReDoc). Sphinx with ``sphinx.ext.autodoc`` is used for offline
HTML documentation – see ``docs/generate_docs.md``.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Tech Support API",
    description="REST backend for the Tech Support application.",
    version="0.1.0",
)
"""FastAPI application instance.

All routes and middleware are registered on this object.
"""

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    return {"message": "Hello World"}
