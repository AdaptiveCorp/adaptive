# ADaptive — API

Web application for generating vulnerable Active Directory infrastructures on Proxmox, designed for penetration testing practice.

---

## Prerequisites

Install system dependencies:

```bash
sudo apt update
sudo apt install python3 npm
```

Install [uv](https://docs.astral.sh/uv/), the Python package and environment manager:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## Installation

Install Python dependencies and create the virtual environment:

```bash
uv sync
```

Copy the example environment file and fill in your configuration:

```bash
cp .env.example .env
```

---

## Running the API

### Database setup

Before starting the API, apply the database migrations to create the required tables:

```bash
uv run alembic upgrade head
```

At least one migration file must exist in `migrations/versions/`. If none is present, generate the initial migration from the SQLAlchemy models defined in `adaptive/api/models/`:

```bash
uv run alembic revision --autogenerate -m "initial"
```

To reset the database and rebuild it from scratch after model changes:

```bash
rm app.db && rm -rf adaptive/migrations/versions/* \
  && uv run alembic revision --autogenerate -m "initial" \
  && uv run alembic upgrade head
```

### Start the server

```bash
# Development mode (auto-reload)
uv run uvicorn adaptive.api.main:app --reload

# Production mode
uv run gunicorn adaptive.api.main:app -k uvicorn.workers.UvicornWorker
```

The API is available at `http://localhost:8000`. The Swagger documentation is accessible at `/docs`.

---

## Running the Frontend

The frontend is located in `adaptive/web/` and is built with React, Vite, and TypeScript.

```bash
# Install dependencies
npm --prefix adaptive/web install

# Development mode (auto-reload)
npm --prefix adaptive/web run dev

# Production build
npm --prefix adaptive/web run build

# Preview the production build
npm --prefix adaptive/web run preview
```

The frontend is available by default at `http://localhost:5173`.

---

## Database Migrations

### Overview

ADaptive uses **Alembic** to manage SQLite database migrations. A migration is a Python script that describes a schema change — adding a table, a column, changing a type, and so on. Each migration has a unique hash identifier and a pointer to the previous migration, forming an ordered chain of all schema changes.

The main benefits are:

- **Version control** — the database schema is versioned alongside the code
- **Reproducibility** — any machine can recreate the exact database state by replaying the migrations in order
- **Collaboration** — each developer generates migrations from their model changes; Alembic applies them in the correct order
- **Rollback** — a problematic migration can be reverted with `downgrade`

### Workflow

The reference schema is defined by the **SQLAlchemy models** in `adaptive/api/models/`. Migration files must never be edited manually.

1. **Modify a model** — add a field, a table, a relation, etc.
2. **Generate the migration** — Alembic compares the models against the current schema and produces the migration script automatically:
   ```bash
   uv run alembic revision --autogenerate -m "description of the change"
   ```
3. **Apply the migration** — runs all pending scripts to bring the database up to date:
   ```bash
   uv run alembic upgrade head
   ```

### Useful Commands

```bash
# Show the currently applied revision
uv run alembic current

# Display the full migration history
uv run alembic history

# Revert the last applied migration
uv run alembic downgrade -1

# Reset the database (delete and recreate)
rm app.db && uv run alembic upgrade head
```

> **Note:** Vulnerability templates are automatically injected at startup from `templates.yaml`.

---

## Template Status

When a template is applied, it can have one of the following statuses:

- `applied`
- `failed`
- `modified`
- `pending`

---

## Linting

Linters are installed automatically with `uv sync` (dev dependency group).

### Ruff (Python)

[Ruff](https://docs.astral.sh/ruff/) handles linting and formatting for Python code. Configuration is defined in `pyproject.toml` under `[tool.ruff]`.

Enabled rule sets: pycodestyle, pyflakes, isort, pyupgrade, bugbear, simplify.

```bash
# Check for lint errors
uv run ruff check .

# Auto-fix lint errors
uv run ruff check . --fix

# Check formatting
uv run ruff format --check .

# Auto-format
uv run ruff format .
```

### yamllint (YAML)

[yamllint](https://yamllint.readthedocs.io/) validates the YAML files in `adaptive/api/database/` (vulnerability templates). Configuration is defined in `.yamllint.yml`.

```bash
uv run yamllint adaptive/api/database/
```

### Pre-commit Check

Run all linters before committing:

```bash
uv run ruff check . --fix && uv run ruff format . && uv run yamllint adaptive/api/database/
```

---

## Docker

Build the image:

```bash
docker build -t adaptive-api .
```

Run the container:

```bash
docker run --rm -p 8000:8000 --env-file .env adaptive-api
```

---

## Tests

The test suite seeds the database with a minimal dataset:

- A VM template
- A project
- A forest
- A domain
- A user

Run the tests with:

```bash
uv run pytest
```
