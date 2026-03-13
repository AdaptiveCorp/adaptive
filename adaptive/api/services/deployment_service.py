import logging
import time

from adaptive.api.infrastructure import AnsibleService, ProxmoxProvider, ServerInfo
from adaptive.api.infrastructure.base import DeploymentResult, HypervisorProvider
from adaptive.api.models.domain import Domain
from adaptive.api.models.project import Project
from adaptive.api.models.server import Server
from adaptive.api.models.user import User
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def _bare_ip(ip: str) -> str:
    return ip.split("/")[0]


def get_dcs_grouped_by_domain(project: Project) -> dict[Domain, list[Server]]:
    grouped: dict[Domain, list[Server]] = {}
    for forest in project.forests:
        for domain in forest.domains:
            dcs = [s for s in domain.servers if s.is_dc]
            if dcs:
                grouped[domain] = dcs
    return grouped


def get_users_grouped_by_domain(project: Project) -> dict[Domain, list[User]]:
    grouped: dict[Domain, list[User]] = {}
    for forest in project.forests:
        for domain in forest.domains:
            if domain.users:
                grouped[domain] = list(domain.users)
    return grouped


def deploy_project(
    project: Project,
    db: Session,
    hypervisor: HypervisorProvider | None = None,
    ansible: AnsibleService | None = None,
) -> DeploymentResult:
    logger.info("Starting deployment for project '%s'", project.name)

    hypervisor = hypervisor or ProxmoxProvider()
    ansible = ansible or AnsibleService(db=db)

    forests = project.forests
    domains: list[Domain] = [d for f in forests for d in f.domains]
    all_servers: list[Server] = [s for d in domains for s in d.servers]

    if not all_servers:
        raise ValueError("No servers in project")

    logger.info(
        "Project '%s': %d forests, %d domains, %d servers",
        project.name,
        len(forests),
        len(domains),
        len(all_servers),
    )

    # --- 1. Clone VMs ---
    server_infos: list[ServerInfo] = [
        ServerInfo(id=s.id, fqdn=s.fqdn, ip=s.ip, gtw=s.gtw, dns=s.dns)
        for s in all_servers
    ]
    clone_results = hypervisor.deploy_lab(server_infos)
    for res in clone_results:
        if res.success and res.vm_id:
            srv: Server | None = db.get(Server, res.server_id)
            if srv:
                srv.vm_id = res.vm_id
                logger.info("Saved vm_id=%d for server '%s'", res.vm_id, srv.fqdn)
    db.commit()

    logger.info("Waiting 60s for VMs to boot...")
    time.sleep(60)

    deployment_result = DeploymentResult(
        project_name=project.name,
        success=True,
        message="Deployment completed",
        clone_results=clone_results,
    )

    # --- 2. DC Promotion ---
    dcs_by_domain = get_dcs_grouped_by_domain(project)

    if dcs_by_domain:
        logger.info("Starting DC promotions across %d domains", len(dcs_by_domain))

    for domain, dcs in dcs_by_domain.items():
        logger.info("Processing domain '%s' (%d DCs)", domain.fqdn, len(dcs))

        for i, dc in enumerate(dcs):
            if not dc.ip:
                logger.error("DC '%s' has no IP, skipping", dc.fqdn)
                continue

            result = ansible.dc_promote(
                server_ip=_bare_ip(dc.ip),
                dc_hostname=dc.fqdn.split(".")[0],
                domain_fqdn=domain.fqdn,
                domain_netbios=domain.fqdn.split(".")[0],
                is_first_dc=(i == 0),
            )

            if not result.success:
                logger.error(
                    "Deployment aborted: DC promotion failed for '%s'", dc.fqdn
                )
                deployment_result.success = False
                deployment_result.error = result.error
                return deployment_result

            if dc.vm_id:
                hypervisor.restart_vm(dc.vm_id)

    # --- 3. Wait for DCs to reboot after promotion ---
    if dcs_by_domain:
        logger.info("Waiting 60s for DCs to reboot after promotion...")
        time.sleep(60)

    # --- 4. Add Users ---
    users_by_domain = get_users_grouped_by_domain(project)

    if users_by_domain:
        logger.info("Starting user creation across %d domains", len(users_by_domain))

    for domain, users in users_by_domain.items():
        # Find a DC for this domain to run the playbook against
        dc = next((s for s in domain.servers if s.is_dc and s.ip), None)
        if not dc:
            logger.error(
                "No reachable DC found for domain '%s', skipping user creation",
                domain.fqdn,
            )
            continue

        logger.info(
            "Adding %d users to domain '%s' via DC '%s'",
            len(users),
            domain.fqdn,
            dc.fqdn,
        )

        user_dicts: list[dict[str, str]] = [
            {"username": u.username, "password": u.password} for u in users
        ]

        result = ansible.add_users(server_ip=_bare_ip(dc.ip), users=user_dicts)

        if not result.success:
            logger.error(
                "User creation failed on domain '%s': %s", domain.fqdn, result.error
            )
            deployment_result.success = False
            deployment_result.error = result.error
            return deployment_result

    logger.info(
        "Deployment completed for project '%s' (success=%s)",
        project.name,
        deployment_result.success,
    )
    return deployment_result
