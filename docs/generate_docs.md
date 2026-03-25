# Generating documentation

This project uses two documentation generators:

| Part | Tool | Output |
|------|------|--------|
| Python backend | Sphinx + autodoc + napoleon | HTML in `docs/_build/html/` |
| TypeScript frontend | TypeDoc | HTML in `docs/frontend/` |

---

## 1. Python – Sphinx

### Prerequisites

Install Sphinx and the required extensions into the project virtual environment:

```bash
cd back
poetry add --group dev sphinx sphinx-autodoc-typehints
```

Or, if you manage dependencies manually:

```bash
pip install sphinx sphinx-autodoc-typehints
```

### Generate HTML

```bash
# From the repository root
sphinx-build -b html docs docs/_build/html
```

Open `docs/_build/html/index.html` in a browser to view the result.

### Regenerate after code changes

Re-run the same command – Sphinx only rebuilds changed files.
To force a full rebuild:

```bash
sphinx-build -b html -E docs docs/_build/html
```

### Create a ZIP archive

```bash
# Windows (PowerShell)
Compress-Archive -Path docs/_build/html -DestinationPath docs/html_docs.zip -Force

# macOS / Linux
zip -r docs/html_docs.zip docs/_build/html
```

---

## 2. TypeScript – TypeDoc

### Prerequisites

```bash
cd front
yarn add --dev typedoc
```

### Generate HTML

```bash
cd front
yarn typedoc --entryPointStrategy expand --entryPoints src --out ../docs/frontend
```

Open `docs/frontend/index.html` in a browser.

### Create a ZIP archive

```bash
# Windows (PowerShell)
Compress-Archive -Path docs/frontend -DestinationPath docs/frontend_docs.zip -Force

# macOS / Linux
zip -r docs/frontend_docs.zip docs/frontend
```

---

## 3. FastAPI built-in OpenAPI docs

No generation needed – available automatically while the server is running:

| URL | Description |
|-----|-------------|
| `http://127.0.0.1:8000/docs` | Swagger UI (interactive) |
| `http://127.0.0.1:8000/redoc` | ReDoc (read-only) |
| `http://127.0.0.1:8000/openapi.json` | Raw OpenAPI JSON schema |

---

## Keeping docs up to date

- Add a docstring to **every** new public function, class, or component before merging.
- Re-run the generators locally before submitting a PR that changes public interfaces.
- Commit updated archives (`html_docs.zip`, `frontend_docs.zip`) together with the code changes.
