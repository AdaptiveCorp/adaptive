import logging
import time
from sqlalchemy.orm import Session
from sqlalchemy import select
from adaptive.api.infrastructure.ansible.ansible_provider import PlaybookResult
from adaptive.api.infrastructure import AnsibleService, ProxmoxProvider, ServerInfo
from adaptive.api.infrastructure.base import DeploymentResult, HypervisorProvider
from adaptive.api.models.applied_template import AppliedTemplate
from adaptive.api.models.domain import Domain
from adaptive.api.models.project import Project
from adaptive.api.models.server import Server
from adaptive.api.models.user import User
from adaptive.api.models.forest import Forest
from adaptive.api.endpoints.utils import get_root_dc
from sqlalchemy.orm import Session
import textwrap
import ast

logger = logging.getLogger(__name__)

def _bare_ip(ip: str) -> str:
    return ip.split("/")[0]

def ansible_deploy_user(user : User, db : Session) :
    ansible = AnsibleService(db=db)

    if user.domain : 
        primary_dc = get_root_dc(user.domain, db)
        
        domain = primary_dc.domain
    
        user_dicts: list[dict[str, str]] = [
            {"username": user.username,
                "firstname": user.firstname,
                "lastname": user.lastname,
                "password": user.password}
        ]
        fqdn = primary_dc.fqdn
        base_dn = "DC="+fqdn.split('.')[-2].lower()+","+"DC="+fqdn.split('.')[-1].lower()
        result = ansible.add_users(server_ip=_bare_ip(primary_dc.ip), users=user_dicts, base_dn=base_dn, domain_fqdn=domain.fqdn)
        return {"succes" : result.success}

    else : 
        print("Erreur la fonction prend que des users de domain")
        result = None
        return result
    

def get_template_for_project(project: Project,db: Session) -> list[AppliedTemplate] :

    stmt = select(AppliedTemplate).where(
        AppliedTemplate.project_id == project.id
    )
    list_stmt = db.scalars(stmt).all()

    return list_stmt

def get_dcs_grouped_by_domain(project: Project) -> dict[Domain, list[Server]]:
    grouped: dict[Domain, list[Server]] = {}
    for forest in project.forests:
        for domain in forest.domains:
            dcs = [s for s in domain.servers if s.is_dc]
            if dcs:
                grouped[domain] = dcs
    return grouped



def get_all_domain_in_project(project: Project, db: Session) -> list[Domain] :
    
    stmt = select(Forest).where(
        Forest.project_id == project.id
    )
    list_foret = db.scalars(stmt).all()
    
    liste_domain = []

    for foret in list_foret :
        stmt = select(Domain).where(
            Domain.forest_id == foret.id
        )
        liste_domain.extend(db.scalars(stmt).all())

    return liste_domain

def get_users_grouped_by_domain(project: Project) -> dict[Domain, list[User]]:
    grouped: dict[Domain, list[User]] = {}
    for forest in project.forests:
        for domain in forest.domains:
            if domain.users:
                grouped[domain] = list(domain.users)
    return grouped

def execute_powershell_winrm(
    server_ip: str,
    powershell_script: str,
    params: dict,
    db: Session,
) -> PlaybookResult:
    ansible = AnsibleService(db=db)

    
    vars_lines = "\n".join(f'    {k}: "{v}"' for k, v in params.items())

    
    indented_script = textwrap.indent(powershell_script.strip(), "        ")

    playbook_content = "\n".join([
        f"- name: Exécuter PowerShell",
        f"  hosts: {server_ip}",
        f"  gather_facts: false",
        f"  vars:",
        vars_lines,                          
        f"    ansible_connection: winrm",
        f"    ansible_winrm_transport: ntlm",
        f"    ansible_winrm_server_cert_validation: ignore",
        f"    ansible_port: 5985",
        f"    ansible_winrm_read_timeout_sec: 120",
        f"",
        f"  tasks:",
        f"    - name: Run PowerShell script",
        f"      win_shell: |",
        indented_script,                     
        f"      register: result",
        f"      ignore_errors: true",
        f"",
        f"    - name: Debug output",
        f"      debug:",
        f"        var: result",
    ])

    return ansible._run_playbook(playbook_content, server_ip, params)


def _step_clone_vms(
    project: Project,
    all_servers: list[Server],
    hypervisor: HypervisorProvider,
    db: Session,
    deployment_result: DeploymentResult,
) -> DeploymentResult:
    logger.info("[STEP 1] Cloning %d VMs for project '%s'", len(all_servers), project.name)

    server_infos: list[ServerInfo] = [
        ServerInfo(id=s.id, fqdn=s.fqdn, ip=s.ip, gtw=s.gtw, dns=s.dns)
        for s in all_servers
    ]
    clone_results = hypervisor.deploy_lab(server_infos)
    deployment_result.clone_results = clone_results

    for res in clone_results:
        if res.success and res.vm_id:
            srv: Server | None = db.get(Server, res.server_id)
            if srv:
                srv.vm_id = res.vm_id
                logger.info("[STEP 1] Saved vm_id=%d for server '%s'", res.vm_id, srv.fqdn)
        else:
            logger.warning("[STEP 1] Clone failed or missing vm_id for server_id=%s", res.server_id)

    db.commit()
    logger.info("[STEP 1] All VMs cloned. Waiting 60s for boot...")
    time.sleep(60)

    return deployment_result


def _step_promote_dcs(
    project: Project,
    hypervisor: HypervisorProvider,
    ansible: AnsibleService,
    deployment_result: DeploymentResult,
) -> DeploymentResult:
    dcs_by_domain = get_dcs_grouped_by_domain(project)

    if not dcs_by_domain:
        logger.info("[STEP 2] No DCs to promote, skipping.")
        return deployment_result

    logger.info("[STEP 2] Starting DC promotions across %d domain(s)", len(dcs_by_domain))

    for domain, dcs in dcs_by_domain.items():
        logger.info("[STEP 2] Processing domain '%s' (%d DC(s))", domain.fqdn, len(dcs))

        for i, dc in enumerate(dcs):
            if not dc.ip:
                logger.error("[STEP 2] DC '%s' has no IP, skipping", dc.fqdn)
                continue

            logger.info(
                "[STEP 2] Promoting DC '%s' (is_first_dc=%s) in domain '%s'",
                dc.fqdn, i == 0, domain.fqdn,
            )
            result = ansible.dc_promote(
                server_ip=_bare_ip(dc.ip),
                dc_hostname=dc.fqdn.split(".")[0],
                domain_fqdn=domain.fqdn,
                domain_netbios=domain.fqdn.split(".")[0],
                is_first_dc=(i == 0),
            )

            if not result.success:
                logger.error("[STEP 2] DC promotion failed for '%s': %s", dc.fqdn, result.error)
                deployment_result.success = False
                deployment_result.error = result.error
                return deployment_result

            logger.info("[STEP 2] DC promotion succeeded for '%s'", dc.fqdn)

            if dc.vm_id:
                logger.info("[STEP 2] Restarting VM id=%d for '%s'", dc.vm_id, dc.fqdn)
                hypervisor.restart_vm(dc.vm_id)

    logger.info("[STEP 2] All DC promotions done. Waiting 60s for reboot...")
    time.sleep(60)

    return deployment_result

def _step_add_users(
    project: Project,
    ansible: AnsibleService,
    deployment_result: DeploymentResult,
) -> DeploymentResult:
    users_by_domain = get_users_grouped_by_domain(project)

    if not users_by_domain:
        logger.info("[STEP 3] No users to create, skipping.")
        return deployment_result

    logger.info("[STEP 3] Starting user creation across %d domain(s)", len(users_by_domain))

    for domain, users in users_by_domain.items():
        dc = next((s for s in domain.servers if s.is_dc and s.ip), None)
        if not dc:
            logger.error("[STEP 3] No reachable DC for domain '%s', skipping", domain.fqdn)
            continue

        fqdn = dc.fqdn
        base_dn = f"DC={fqdn.split('.')[-2].lower()},DC={fqdn.split('.')[-1].lower()}"

        user_dicts: list[dict[str, str]] = [
            {
                "username": u.username,
                "firstname": u.firstname,
                "lastname": u.lastname,
                "password": u.password,
            }
            for u in users
        ]

        logger.info(
            "[STEP 3] Adding %d user(s) to domain '%s' via DC '%s'",
            len(users), domain.fqdn, dc.fqdn,
        )
        result = ansible.add_users(
            server_ip=_bare_ip(dc.ip),
            users=user_dicts,
            base_dn=base_dn,
            domain_fqdn=domain.fqdn,
        )

        if not result.success:
            logger.error("[STEP 3] User creation failed on '%s': %s", domain.fqdn, result.error)
            deployment_result.success = False
            deployment_result.error = result.error
            return deployment_result

        logger.info("[STEP 3] Users successfully created on domain '%s'", domain.fqdn)

    return deployment_result


def _step_push_vulnerabilities(
    project: Project,
    db: Session,
    deployment_result: DeploymentResult,
) -> DeploymentResult:
    liste_templates = get_template_for_project(project, db)
    liste_domain = get_all_domain_in_project(project, db)

    vuln_templates = [
        t for t in liste_templates
        if t.template.category != "infrastructure" and t.status == "applied"
    ]

    if not vuln_templates:
        logger.info("[STEP 4] No vulnerability templates to apply, skipping.")
        return deployment_result

    logger.info(
        "[STEP 4] Pushing %d vulnerability template(s) across %d domain(s)",
        len(vuln_templates), len(liste_domain),
    )

    for domain in liste_domain:
        dc = get_root_dc(domain, db)

        for template in vuln_templates:
            logger.info(
                "[STEP 4] Applying template '%s' on DC '%s' (domain '%s')",
                template.template.code, dc.fqdn, domain.fqdn,
            )
            param_vuln = ast.literal_eval(template.params)
            powershell_script = template.template.content

            result = execute_powershell_winrm(dc.ip, powershell_script, param_vuln, db)

            if not result.success:
                logger.error(
                    "[STEP 4] Template '%s' failed on '%s': %s",
                    template.template.code, dc.fqdn, result.error,
                )
                deployment_result.success = False
                deployment_result.error = result.error
                return deployment_result

            logger.info(
                "[STEP 4] Template '%s' applied successfully on '%s'",
                template.template.code, dc.fqdn,
            )

    return deployment_result

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
        project.name, len(project.forests), len(domains), len(all_servers),
    )

    deployment_result = DeploymentResult(
        project_name=project.name,
        success=True,
        message="Deployment completed",
    )

    steps = [
        lambda r: _step_clone_vms(project, all_servers, hypervisor, db, r),
        lambda r: _step_promote_dcs(project, hypervisor, ansible, r),
        lambda r: _step_add_users(project, ansible, r),
        lambda r: _step_push_vulnerabilities(project, db, r),
    ]

    for step in steps:
        deployment_result = step(deployment_result)
        if not deployment_result.success:
            logger.error("[DEPLOY] Deployment aborted at step: %s", step.__name__ if hasattr(step, '__name__') else str(step))
            return deployment_result

    logger.info(
        "[DEPLOY] Deployment completed for project '%s' (success=%s)",
        project.name, deployment_result.success,
    )
    return deployment_result
