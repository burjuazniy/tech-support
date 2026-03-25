# Tech Support

Project for bachelor graduation thesis.

Stack: **FastAPI** (Python 3.10–3.11) + **React + TypeScript** (Vite, Yarn).

---

## Table of contents

1. [Prerequisites](#1-prerequisites)
2. [Clone the repository](#2-clone-the-repository)
3. [Backend setup](#3-backend-setup)
4. [Frontend setup](#4-frontend-setup)
5. [Running in development mode](#5-running-in-development-mode)
6. [Common commands](#6-common-commands)
7. [Documentation standards](#7-documentation-standards)

---

## 1. Prerequisites

Install the following tools before you begin. Links point to official download pages.

### Git

```bash
# Verify after install:
git --version
```

Download: https://git-scm.com/downloads

### Python 3.10 or 3.11

The backend requires Python **>=3.10, <3.12**.

```bash
# Verify:
python --version   # or python3 --version
```

Download: https://www.python.org/downloads/
> On Windows, tick **"Add Python to PATH"** during setup.

### Poetry (Python dependency manager)

```bash
# Install (all platforms):
pip install poetry

# Verify:
poetry --version
```

### Node.js 20 LTS

Yarn needs Node.js to run.

```bash
# Verify:
node --version
npm --version
```

Download: https://nodejs.org/en/download (choose **LTS**)

### Yarn (package manager)

```bash
npm install -g yarn

# Verify:
yarn --version
```

---

## 2. Clone the repository

```bash
git clone https://github.com/burjuazniy/tech-support.git
cd tech-support
```

---

## 3. Backend setup

All backend commands are run from the `back/` directory.

```bash
cd back
```

### Install dependencies

```bash
poetry install
```

Poetry creates a virtual environment automatically (`.venv/` inside `back/`).

### Environment variables

The project does not require an `.env` file at this stage. If one is needed in the future, copy the example:

```bash
cp .env.example .env   # then edit .env as needed
```

---

## 4. Frontend setup

All frontend commands are run from the `front/` directory.

```bash
cd front
```

### Install dependencies

```bash
yarn install
```

---

## 5. Running in development mode

Open **two terminal windows** - one for the backend, one for the frontend.

### Terminal 1 - Backend

```bash
cd back
python run.py
```

The API starts at **http://127.0.0.1:8000**.
Interactive API docs are available at:

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000/docs | Swagger UI |
| http://127.0.0.1:8000/redoc | ReDoc |

### Terminal 2 - Frontend

```bash
cd front
yarn dev
```

The app opens at **http://localhost:5173**.

The frontend is configured to proxy requests to the backend at `http://localhost:5173`.

---

## 6. Common commands

### Backend

| Command | Description |
|---------|-------------|
| `poetry install` | Install / sync all dependencies |
| `poetry add <pkg>` | Add a runtime dependency |
| `poetry add --group dev <pkg>` | Add a dev-only dependency |
| `python run.py` | Start dev server with hot-reload |
| `poetry run pytest` | Run tests |

### Frontend

| Command | Description |
|---------|-------------|
| `yarn install` | Install / sync all dependencies |
| `yarn dev` | Start Vite dev server |
| `yarn build` | Build for production (`dist/`) |
| `yarn preview` | Preview production build locally |
| `yarn lint` | Run ESLint |

### Documentation

```bash
# Generate Sphinx HTML docs (from repo root)
poetry -C back run sphinx-build -b html docs docs/_build/html

# Open result
open docs/_build/html/index.html        # macOS
start docs/_build/html/index.html       # Windows
```

See [docs/generate_docs.md](docs/generate_docs.md) for full instructions including TypeDoc.

---

## 7. Documentation standards

### Python (backend)

We follow **Google-style docstrings** (PEP 257 + Google Python Style Guide).
Every public module, class, function, and module-level constant must have a docstring.

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

**What to document:** all `@app.<method>` route handlers (include `summary=`, `tags=[]`),
Pydantic models, helper functions, and module-level constants.

**Tools:** Sphinx + autodoc + napoleon (offline HTML), FastAPI built-in OpenAPI (`/docs`, `/redoc`).

### TypeScript / React (frontend)

We follow **TSDoc** (compatible with JSDoc tooling).
Every exported component, hook, function, and constant must have a TSDoc comment.

```tsx
/**
 * Short one-line summary.
 *
 * @param props - Describe props.
 * @returns The rendered JSX element.
 *
 * @example
 * ```tsx
 * <MyComponent title="Hello" />
 * ```
 */
export function MyComponent({ title }: Props) { ... }
```

**Tools:** TypeDoc - see [docs/generate_docs.md](docs/generate_docs.md).
