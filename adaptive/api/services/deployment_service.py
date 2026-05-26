import logging
import time
from collections.abc import Callable

from sqlalchemy.orm import Session

from adaptive.api.infrastructure import AnsibleService, ProxmoxProvider, ServerInfo
from adaptive.api.infrastructure.base import DeploymentResult, HypervisorProvider
from adaptive.api.models.domain import Domain
from adaptive.api.models.project import Project
from adaptive.api.models.server import Server, ServerStatus
from adaptive.api.services.applied_template import get_pending_reverted_template
from adaptive.api.services.groups import (
    _step_add_group_members,
    _step_add_groups,
    get_groups_not_push_by_domain,
)
from adaptive.api.services.servers import _step_promote_dcs, get_dcs_to_promote
from adaptive.api.services.users import _step_add_users, get_users_not_push_by_domain
from adaptive.api.services.vulnerabilities import (
    _step_push_vulnerabilities,
    _step_reverse_templates,
)

logger: logging.Logger = logging.getLogger(__name__)


def _step_clone_vms(
    project: Project,
    all_servers: list[Server],
    hypervisor: HypervisorProvider,
    db: Session,
    deployment_result: DeploymentResult,
) -> DeploymentResult:

    logger.info("[STEP 1] Cloning %d VMs for project '%s'", len(all_servers), project.name)

    server_infos: list[ServerInfo] = [
        ServerInfo(
            id=s.id,
            fqdn=s.fqdn,
            ip=s.ip,
            gtw=s.gtw,
            dns=s.dns,
            template_vm_id=s.vm_template.vm_id if s.vm_template else None,
        )
        for s in all_servers
    ]

    clone_results = hypervisor.deploy_lab(server_infos)
    deployment_result.clone_results = clone_results

    for res in clone_results:
        srv: Server | None = db.get(Server, res.server_id)
        if res.success and res.vm_id:
            if srv:
                srv.vm_id = res.vm_id
                srv.status = ServerStatus.APPLIED
                logger.info("[STEP 1] Saved vm_id=%d for server '%s'", res.vm_id, srv.fqdn)
        else:
            if srv:
                srv.status = ServerStatus.ERROR
            logger.warning("[STEP 1] Clone failed or missing vm_id for server_id=%s", res.server_id)

    db.commit()
    logger.info("[STEP 1] All VMs cloned. Waiting 60s for boot...")

    time.sleep(30)

    return deployment_result


def build_deployment_steps(
    project: Project,
    all_servers: list[Server],
    hypervisor: HypervisorProvider,
    ansible: AnsibleService,
    db: Session,
) -> list[Callable[[DeploymentResult], DeploymentResult]]:
    steps: list[Callable[[DeploymentResult], DeploymentResult]] = []

    servers_to_clone = [s for s in all_servers if s.status != ServerStatus.APPLIED]

    if servers_to_clone:
        steps.append(lambda r, s=servers_to_clone: _step_clone_vms(project, s, hypervisor, db, r))

    servers_to_promote = get_dcs_to_promote(project, db)

    if servers_to_promote:
        steps.append(
            lambda r: _step_promote_dcs(project, hypervisor, ansible, servers_to_promote, db, r)
        )

    users_not_pushed = get_users_not_push_by_domain(project, db)
    if any(users_list for users_list in users_not_pushed.values()):
        steps.append(lambda r: _step_add_users(project, ansible, db, users_not_pushed, r))

    groups_not_pushed = get_groups_not_push_by_domain(project, db)
    if any(gl for gl in groups_not_pushed.values()):
        steps.append(lambda r: _step_add_groups(project, ansible, db, groups_not_pushed, r))

    if any(gl for gl in groups_not_pushed.values()):
        steps.append(lambda r: _step_add_group_members(project, ansible, db, groups_not_pushed, r))

    find_pending_reverted_template = get_pending_reverted_template(project, db)
    if find_pending_reverted_template:
        steps.append(
            lambda r: _step_reverse_templates(
                project, ansible, db, find_pending_reverted_template, r
            )
        )

    steps += [
        lambda r: _step_push_vulnerabilities(project, db, r),
    ]

    return steps


def deploy_project(
    project: Project,
    db: Session,
    hypervisor: HypervisorProvider | None = None,
    ansible: AnsibleService | None = None,
) -> DeploymentResult:

    logger.info("[DEPLOY] Starting deployment for project '%s'", project.name)

    hypervisor = hypervisor or ProxmoxProvider()
    ansible = ansible or AnsibleService(db=db)

    domains: list[Domain] = [d for f in project.forests for d in f.domains]
    all_servers: list[Server] = [s for d in domains for s in d.servers]

    if not all_servers:
        raise ValueError(f"No servers found in project '{project.name}'")

    logger.info(
        "[DEPLOY] Project '%s': %d forest(s), %d domain(s), %d server(s)",
        project.name,
        len(project.forests),
        len(domains),
        len(all_servers),
    )

    deployment_result = DeploymentResult(
        project_name=project.name,
        success=True,
        message="Deployment completed",
    )

    steps = build_deployment_steps(project, all_servers, hypervisor, ansible, db)

    for step in steps:
        deployment_result = step(deployment_result)
        if not deployment_result.success:
            logger.error(
                "[DEPLOY] Deployment aborted at step: %s",
                step.__name__ if hasattr(step, "__name__") else str(step),
            )
            return deployment_result

    logger.info(
        "[DEPLOY] Deployment completed for project '%s' (success=%s)",
        project.name,
        deployment_result.success,
    )
    return deployment_result
