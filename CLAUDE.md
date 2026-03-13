# CLAUDE.md

## Project

**ADaptive** — Web application for generating vulnerable cyber-attack
infrastructures. Creates Active Directory labs on Proxmox for pentester
training. Users define an AD infrastructure (Project → Forest → Domain →
Server / User / Vulnerability), then deploy it: VMs are cloned from Packer
templates, bootstrapped via cloud-init, and configured through Ansible over
WinRM (DC promotion, user creation, vulnerability injection).

Working directory: `api/`

## Stack

- Python/FastAPI, SQLAlchemy + Alembic (SQLite), pydantic-settings
- Packer (Windows Server on Proxmox via `proxmox-iso`), Ansible via ansible-runner + pywinrm
- Proxmox API via proxmoxer, Cloudbase-Init for cloud-init on Windows
- Frontend: TypeScript in `adaptive/web/` (planned, stack TBD)

## Non-negotiable rules

- All Python commands via `uv run` — never bare `python` or `pip`
- SQLAlchemy models are the **sole source of truth** for schema
- Never edit Alembic migrations manually — always `alembic revision --autogenerate`
- Ansible playbook modules: always use FQCNs (`ansible.windows.win_feature`, etc.)
- `ansible-runner` expects playbooks in `{tmpdir}/project/` with relative filename
- Proxmox clone: always fetch `newid` from `/cluster/nextid` before cloning
- Code and comments in English; project docs may be in French

## Load these docs before working on related areas

- `agent_docs/architecture.md` → data model, API layers, service patterns
- `agent_docs/deployment_flow.md` → clone → DC promo → users → vulns workflow
- `agent_docs/vulnerability_system.md` → template system, PowerShell snippets
- `agent_docs/packer_templates.md` → Packer build, autounattend, WinRM, Cloudbase
- `agent_docs/dev_commands.md` → all uv / alembic / packer / ansible commands
