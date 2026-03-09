import logging
import time

from sqlalchemy.orm import Session

from adaptive.infrastructure import AnsibleService, ProxmoxProvider, ServerInfo
from adaptive.models.domain import Domain
from adaptive.models.server import Server

logger = logging.getLogger(__name__)


def get_dcs_grouped_by_domain(db: Session) -> dict[int, list[Server]]:
    dcs = (
        db.query(Server)
        .filter(Server.is_dc)
        .order_by(Server.domain_id, Server.id)
        .all()
    )
    grouped: dict[int, list[Server]] = {}
    for dc in dcs:
        grouped.setdefault(dc.domain_id, []).append(dc)
    return grouped


def deploy_project(
    project,
    db: Session,
    hypervisor: ProxmoxProvider | None = None,
    ansible: AnsibleService | None = None,
) -> dict:
    hypervisor = hypervisor or ProxmoxProvider()
    ansible = ansible or AnsibleService()

    forests = project.forests
    domains = [d for f in forests for d in f.domains]
    all_servers = [s for d in domains for s in d.servers]

    if not all_servers:
        raise ValueError("No servers in project")

    # --- Clone VMs ---
    server_infos = [
        ServerInfo(id=s.id, fqdn=s.fqdn, ip=s.ip, vm_id=s.vm_id)
        for s in all_servers
    ]
    clone_results = hypervisor.deploy_lab(server_infos)

    for res in clone_results:
        if res.success and res.vm_id:
            server = db.get(Server, res.server_id)
            if server:
                server.vm_id = res.vm_id
    db.commit()

    logger.info("Waiting 60s for VMs to boot...")
    time.sleep(60)

    # --- DC Promotion ---
    dcs_by_domain = get_dcs_grouped_by_domain(db)
    last_result: dict = {"success": True, "message": "No DCs to promote"}

    for domain_id, dcs in dcs_by_domain.items():
        domain = db.get(Domain, domain_id)
        if not domain:
            continue

        for i, dc in enumerate(dcs):
            is_first = i == 0
            result = ansible.dc_promote(
                server_ip=dc.ip,
                dc_hostname=dc.fqdn,
                domain_fqdn=domain.fqdn,
                domain_netbios=domain.fqdn.split(".")[0],
                is_first_dc=is_first,
            )

            last_result = {"success": result.success, "error": result.error}

            if result.success:
                hypervisor.restart_vm(dc.vm_id)
            else:
                logger.error("DC promotion failed for %s: %s", dc.fqdn, result.error)
                return {"project": project.name, "deployment_result": last_result}

    return {"project": project.name, "deployment_result": last_result}
