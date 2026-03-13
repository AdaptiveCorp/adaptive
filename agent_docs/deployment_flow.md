# Deployment Flow

## Overview

`deployment_service.py` orchestrates the full lab deployment sequence.
Triggered via `POST /projects/{project_id}/deploy`.

## Step-by-Step

1. **Clone VMs from template**
   - For each server in the project:
     - Call Proxmox API: fetch `newid` from `/cluster/nextid`
     - Clone template to new VM with the fetched `newid`
     - Configure cloud-init networking (IP, gateway, DNS) via `_configure_cloudinit()`
     - Start VM and wait for boot
   - Store `vm_id` on the `Server` model

2. **Promote Domain Controllers**
   - Group servers by domain (`get_dcs_grouped_by_domain()`)
   - For each domain's DC(s):
     - First DC: create forest with `Install-ADDSForest` (via "dc_promo" template)
     - Additional DCs: join domain with `Install-ADDSDomainController`
   - Restart VM after promotion
   - Wait 60s for DC reboot

3. **Create AD users**
   - Group users by domain (`get_users_grouped_by_domain()`)
   - For each domain with users:
     - Find a reachable DC (has IP + `is_dc=True`)
     - Run "add_users" config template via `AnsibleService.add_users()`
     - Users defined in `Domain.users` relationship

4. **Apply vulnerability configurations**
   - Iterate `AppliedTemplate` entries of type `vulnerability`
   - Run PowerShell snippets via `AnsibleService` on target entity

## Helper Functions

- `get_dcs_grouped_by_domain(project)` → `dict[Domain, list[Server]]`
- `get_users_grouped_by_domain(project)` → `dict[Domain, list[User]]`
- `_bare_ip(ip)` → strips CIDR notation (e.g., "10.0.0.1/24" → "10.0.0.1")

## AnsibleService Constraints

- ansible-runner expects playbooks at `{tmpdir}/project/<playbook.yml>`
- Path must be a relative filename, not absolute
- WinRM must be reachable before any playbook runs
- Templates fetched from DB by `code` field; raises `FileNotFoundError` if missing

## Error Handling Pattern

- Deployment aborts on first failure
- DB transaction rolled back on exception
- All steps logged with context (server IDs, FQDNs, vm_ids)

Raise explicit exceptions with context:

    raise DeploymentError(
        f"DC promo failed for server {server.id} (vm_id={server.vm_id}): {detail}"
    )
