# Development Commands

## Python / FastAPI

    # Run the API server (development)
    uv run uvicorn adaptive.api.main:app --reload

    # Run with gunicorn (production-like)
    uv run gunicorn adaptive.api.main:app -k uvicorn.workers.UvicornWorker

    # Add a dependency
    uv add <package>

    # Sync environment
    uv sync

## Alembic (Migrations)

    # Generate migration from model changes
    uv run alembic revision --autogenerate -m "description"

    # Apply all pending migrations
    uv run alembic upgrade head

    # Downgrade one step
    uv run alembic downgrade -1

    # Show current revision
    uv run alembic current

    # Show migration history
    uv run alembic history

**Never edit migrations manually** — always autogenerate from model changes.

## Packer

    # Initialize Packer plugins
    packer init packer/windows-server-2022/

    # Validate template
    packer validate -var-file=packer/creds.pkrvars.hcl packer/windows-server-2022/

    # Build template
    packer build -var-file=packer/creds.pkrvars.hcl packer/windows-server-2022/

    # Build with debug (step-by-step)
    PACKER_LOG=1 packer build -debug -var-file=packer/creds.pkrvars.hcl packer/windows-server-2022/

## Ansible (standalone testing)

    # Test WinRM connectivity
    uv run python -c "import winrm; s=winrm.Session('https://<ip>:5986/wsman', auth=('Administrator','<pass>'), transport='ntlm', server_cert_validation='ignore'); print(s.run_cmd('hostname'))"

    # Run a playbook via ansible-runner (rarely done manually — use the API)
    uv run ansible-runner run <private_data_dir> -p playbook.yml

## Linting / Formatting (Ruff)

    # Check for lint errors
    uv run ruff check .

    # Auto-fix lint errors
    uv run ruff check . --fix

    # Check formatting
    uv run ruff format --check .

    # Auto-format
    uv run ruff format .

    # Full lint + format before commit
    uv run ruff check . --fix && uv run ruff format .

Config in `pyproject.toml` under `[tool.ruff]`.

Enabled rule sets:
- `E` / `W` — pycodestyle (style errors & warnings)
- `F` — pyflakes (unused imports, undefined names)
- `I` — isort (import ordering)
- `UP` — pyupgrade (modernize syntax to Python 3.12+)
- `B` — flake8-bugbear (common bugs & design issues)
- `SIM` — flake8-simplify (simplifiable constructs)

Ignored: `B008` — `Depends()` in argument defaults is required by FastAPI's DI.

## YAML Linting (yamllint)

    # Lint all YAML files
    uv run yamllint adaptive/api/database/

    # Lint a specific file
    uv run yamllint adaptive/api/database/templates.yaml

Config in `.yamllint.yml`:
- Line length: 140 (accommodates embedded PowerShell/Ansible blocks in `content: |`)
- `document-start` disabled (no `---` required at top of file)
- `truthy` check on keys disabled (allows `yes`/`no` in Ansible playbooks)

## Database

    # Reset DB (delete and recreate)
    rm app.db && uv run alembic upgrade head

    # Templates are seeded automatically at app startup from templates.yaml
