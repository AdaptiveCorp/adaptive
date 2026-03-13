# Architecture — ADaptive API

## API Layers

| Layer          | Path                           | Responsibility                               |
| -------------- | ------------------------------ | -------------------------------------------- |
| Endpoints      | `adaptive/api/endpoints/`      | FastAPI routers, nested REST routes          |
| Models         | `adaptive/api/models/`         | SQLAlchemy ORM — source of truth for schema  |
| Services       | `adaptive/api/services/`       | Business logic, deployment orchestration     |
| Infrastructure | `adaptive/api/infrastructure/` | External integrations behind ABCs            |
| Environment    | `adaptive/api/environment/`    | pydantic-settings config + DB engine/session |
| Database       | `adaptive/api/database/`       | Template seeding from `templates.yaml`       |

## REST Route Structure

Nested routes pattern:

    /projects/{id}/forests/{id}/domains/{id}/servers

Standalone routes:

    /users/                          (linked to domain or server)
    /vulnerabilities/                (template catalog + applied vulns)
    /health                          (healthcheck)

## Data Model

    Project
      └── Forest (fqdn)
            └── Domain (fqdn)
                  ├── Server  (fqdn, is_dc, vm_id, ip, gtw, dns, parent_id → Server)
                  └── User    (username, password, linked to domain OR server)

    Template (code, type: "config" | "vulnerability", category, content, required_params)
      └── AppliedTemplate
            ├── project_id  → Project  (required)
            ├── template_id → Template (required)
            ├── user_id     → User     (nullable)
            ├── domain_id   → Domain   (nullable)
            ├── server_id   → Server   (nullable)
            ├── forest_id   → Forest   (nullable)
            └── params      (JSON text, nullable)

Key notes:
- `Server.parent_id` allows self-referencing hierarchy (child servers)
- `User` links to either `domain_id` or `server_id`, not both (endpoint validates)
- `AppliedTemplate` uses explicit FK columns per entity type (not polymorphic entity_id/entity_type)

## Infrastructure Abstractions

- `HypervisorProvider` (ABC) → `ProxmoxProvider`
  - `deploy_lab()`, `clone_vm()`, `start_vm()`, `restart_vm()`, `stop_vm()`
  - Clone configures cloud-init networking (IP, gateway, DNS) via Proxmox API
- `AnsibleService` runs playbooks stored as DB templates via ansible-runner
  - `dc_promote()` — fetches "dc_promo" template, runs with WinRM
  - `add_users()` — fetches "add_users" template, batch-creates AD users
  - `_run_playbook()` — creates tmpdir, writes playbook, builds inventory, runs ansible-runner

## Key Constraints

- DB is SQLite (`app.db`) — never use raw SQL, always go through SQLAlchemy ORM
- Config loaded from `.env` via pydantic-settings — add new vars to `.env.example` too
- Templates seeded from `templates.yaml` at app startup via FastAPI lifespan event (upsert logic)
- No authentication/authorization layer yet
