# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ADaptive** is a pentest lab generator. It automates the creation of vulnerable Active Directory environments on Proxmox for security training and offensive security practice.

The workflow:
1. **Packer** builds Windows Server VM templates (with WinRM, VirtIO drivers, Cloudbase-Init) on Proxmox.
2. The **API** (FastAPI) orchestrates lab deployment: clone VMs from templates → promote Domain Controllers → join machines to domains → create AD users → apply vulnerability configurations (Kerberoasting, DCSync, AS-REP Roasting, etc.).
3. A **web frontend** (planned, TypeScript — stack TBD) will live in `adaptive/web/`.

The goal: one-click deployment of realistic, purposely vulnerable AD infrastructures for pentesting practice.

## Repository Structure

```
ADaptiveBYOL/
└── api/                    ← current working directory
    ├── adaptive/api/       ← FastAPI application
    │   ├── endpoints/      ← REST routers
    │   ├── models/         ← SQLAlchemy ORM models (DB schema source of truth)
    │   ├── services/       ← Business logic (deployment orchestration)
    │   ├── infrastructure/ ← External integrations (Proxmox, Ansible)
    │   ├── environment/    ← Config (pydantic-settings) & DB setup
    │   └── database/       ← Template seeding from templates.yaml
    ├── packer/             ← Packer templates for Windows Server VM images
    │   ├── windows-server-2022.pkr.hcl
    │   ├── variables.pkr.hcl
    │   ├── creds.pkr.hcl
    │   ├── http/           ← autounattend.xml for unattended Windows install
    │   └── scripts/        ← Post-install scripts (WinRM, VirtIO, Cloudbase, cleanup)
    ├── migrations/         ← Alembic migrations (auto-generated, do not edit manually)
    └── cli/                ← CLI tooling (TBD)
```

## Commands

```bash
# Install dependencies
uv sync

# Run dev server
uv run uvicorn adaptive.main:app --reload

# Run migrations
uv run alembic upgrade head

# Auto-generate a new migration from model changes
uv run alembic revision --autogenerate -m "description"

# Reset database (SQLite)
rm app.db && uv run alembic upgrade head

# Seed templates (done automatically on app startup, or manually)
uv run python -c "from adaptive.database.seed_templates import seed_templates; seed_templates()"
```

### Packer (VM template builds)

```bash
# Build a Windows Server 2022 template on Proxmox
cd packer/
packer init .
packer build -var-file=creds.pkr.hcl windows-server-2022.pkr.hcl
```

### Ansible (required collections)

```bash
uv tool install ansible-core --with pywinrm
ansible-galaxy collection install ansible.windows community.windows
```

## Architecture

### API Layers

- **`endpoints/`** — FastAPI routers. Nested REST routes: `/projects/{id}/forests/{id}/domains/{id}/servers`.
- **`models/`** — SQLAlchemy ORM models. Alembic generates migrations from these — never edit migrations manually.
- **`services/`** — Business logic. `deployment_service.py` orchestrates: clone VMs → promote DCs → create users → apply vulnerabilities.
- **`infrastructure/`** — External integrations behind ABCs. `HypervisorProvider` → `ProxmoxProvider`. `AnsibleService` runs playbooks from DB templates.
- **`environment/`** — Config (`pydantic-settings` from `.env`) and SQLAlchemy engine/session setup.
- **`database/`** — Template seeding from `templates.yaml` on app startup via FastAPI lifespan.

### Data Model

```
Project → Forest → Domain → Server (is_dc flag, vm_id from Proxmox)
                          → User
Template (type: config | vulnerability) → AppliedTemplate (links to Project + any entity)
```

### Template System

Two types in `templates.yaml`:

- **config**: Full Ansible playbooks (dc_promo, add_users, domain_join) — used by `AnsibleService` at deploy time.
- **vulnerability**: PowerShell snippets for AD attack scenarios (Kerberoasting, DCSync, AS-REP Roasting, Golden Ticket, etc.).

Modules in playbooks must use FQCNs (e.g. `ansible.windows.win_feature`, `community.windows.win_domain_user`).

### Packer Templates

Windows Server VM templates built with Packer on Proxmox. The build process:
1. Boots from ISO with `autounattend.xml` for unattended install.
2. Runs post-install scripts: VirtIO drivers, WinRM setup, Cloudbase-Init.
3. Produces a Proxmox template ready to be cloned by the API.

## Key Conventions

- All Python commands prefixed with `uv run` (uv-managed venv).
- SQLAlchemy models are the source of truth — regenerate migrations with `alembic revision --autogenerate`.
- `ansible-runner` expects playbooks in `{tmpdir}/project/` subdirectory with relative filename.
- Proxmox clone requires `newid` from `/cluster/nextid` API.
- Config via `.env` file (see `.env.example`). DB is SQLite (`app.db`).
- Language: code and comments in English; project documentation may be in French.
