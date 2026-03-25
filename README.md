# Tech Support

Project for bachelor graduation thesis.

Stack: **FastAPI** (Python) + **React + TypeScript** (Vite + Yarn).

---

## Documentation standards

### Python (backend)

We follow **Google-style docstrings** (PEP 257 + Google Python Style Guide).
Every public module, class, function, and module-level constant must have a docstring.

**Module docstring** - describe purpose, note standards used, and list any CLI usage:

```python
"""Short one-line summary.

Longer description if needed.

Standards: Google-style docstrings.
"""
```

**Function / method docstring**:

```python
def create_ticket(title: str, body: str) -> dict:
    """Create a new support ticket.

    Args:
        title: Short summary of the issue (max 120 chars).
        body: Full description of the problem.

    Returns:
        dict[str, Any]: The newly created ticket object.

    Raises:
        ValueError: If ``title`` is empty.

    Example:
        >>> create_ticket("Login broken", "Cannot log in since update.")
        {'id': 1, 'title': 'Login broken', ...}
    """
```

**What to document:**
- All `@app.<method>` route handlers - include `summary=`, `tags=[]`, and a full docstring.
- Pydantic models and their fields.
- Any helper / utility functions.
- Module-level constants that affect behaviour (e.g. `DEBUG`).

**Tools:**
- **Sphinx + autodoc + napoleon** - offline HTML docs from docstrings. See [`docs/generate_docs.md`](docs/generate_docs.md).
- **FastAPI built-in OpenAPI** - interactive docs at `/docs` (Swagger UI) and `/redoc` while the server is running. No extra setup needed.

---

### TypeScript / React (frontend)

We follow **TSDoc** (compatible with JSDoc tooling).
Every exported function, component, hook, type, and constant must have a TSDoc comment.

**Component docstring**:

```tsx
/**
 * Short one-line summary.
 *
 * Longer description if needed.
 *
 * @param props - Describe props object or each prop with `@param props.foo`.
 * @returns The rendered JSX element.
 *
 * @example
 * ```tsx
 * <MyComponent title="Hello" />
 * ```
 */
export function MyComponent({ title }: Props) { ... }
```

**File-level docblock** (use `@file` / `@module` tags):

```tsx
/**
 * @file Application bootstrap - mounts the React tree into the DOM.
 * @module main
 */
```

**What to document:**
- All exported React components and hooks.
- All exported utility functions and constants.
- Entry-point files (`main.tsx`).

**Tools:**
- **TypeDoc** - generates HTML from TSDoc comments. See [`docs/generate_docs.md`](docs/generate_docs.md).

---

## Quick start

```bash
# Backend
cd back
poetry install
python run.py          # http://127.0.0.1:8000 | /docs | /redoc

# Frontend
cd front
yarn install
yarn dev               # http://localhost:5173
```