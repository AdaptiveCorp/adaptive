import ast
import json
import logging
import textwrap
import time

import winrm
from sqlalchemy import select, exists
from sqlalchemy.orm import Session

from adaptive.api.endpoints.utils import get_root_dc
from adaptive.api.environment.config import settings
from adaptive.api.infrastructure import AnsibleService, ProxmoxProvider, ServerInfo
from adaptive.api.infrastructure.ansible.ansible_provider import PlaybookResult
from adaptive.api.infrastructure.base import DeploymentResult, HypervisorProvider
from adaptive.api.models.applied_template import AppliedTemplate, TemplateStatus
from adaptive.api.models.domain import Domain
from adaptive.api.models.forest import Forest
from adaptive.api.models.project import Project
from adaptive.api.models.server import Server, ServerStatus
from adaptive.api.models.template import Template
from adaptive.api.models.user import User
from adaptive.api.models.group import Group
from adaptive.api.exceptions import (
    AppliedTemplateNotFoundError
)
from collections.abc import Callable

logger = logging.getLogger(__name__)


def _bare_ip(ip: str) -> str:
    return ip.split("/")[0]


def _wait_for_adws(
    server_ip: str,
    timeout: int = 45,
    poll_interval: int = 15,
    initial_wait: int = 30,
) -> bool:
    
    """Poll a DC via WinRM until connection is successful, then enable ADWS."""
    if initial_wait:
        logger.info("[WAIT] Waiting %ds before checking WinRM on %s...", initial_wait, server_ip)
        time.sleep(initial_wait)

    session = winrm.Session(
        f"http://{server_ip}:5985/wsman",
        auth=(settings.ansible_user, settings.ansible_password),
        transport="ntlm",
    )

    elapsed = 0

    while elapsed < timeout:
        try:
            result = session.run_ps("echo ok")
            if result.status_code == 0:
                logger.info("[WAIT] WinRM is reachable on %s (after %ds)", server_ip, elapsed + initial_wait)

                # Activer et démarrer ADWS
                logger.info("[WAIT] Enabling and starting ADWS on %s...", server_ip)
                adws_result = session.run_ps(
                    "Set-Service ADWS -StartupType Automatic; Start-Service ADWS"
                )

                if adws_result.status_code == 0:
                    logger.info("[WAIT] ADWS successfully started on %s", server_ip)
                else:
                    error_msg = adws_result.std_out.decode(errors="replace").strip()
                    logger.error("[WAIT] Failed to start ADWS on %s: %s", server_ip, error_msg)
                    return False

                return True

        except Exception as exc:
            logger.info("[WAIT] Cannot reach %s yet (%s), retrying in %ds...", server_ip, type(exc).__name__, poll_interval)

        time.sleep(poll_interval)
        elapsed += poll_interval

    logger.error("[WAIT] Timeout (%ds) waiting for WinRM on %s", timeout + initial_wait, server_ip)
    return False


def _wait_for_ad_ready(
    server_ip: str,
    timeout: int = 600,        # promotion AD peut être longue, 10 min n'est pas déraisonnable
    poll_interval: int = 30,
    initial_wait: int = 60,    # tu peux garder 30, mais 60 est plus safe
) -> bool:
    """Attendre que le DC soit réellement fonctionnel (AD DS + ADWS)."""

    if initial_wait:
        logger.info("[WAIT] Waiting %ds before checking AD on %s...", initial_wait, server_ip)
        time.sleep(initial_wait)

    session = winrm.Session(
        f"http://{server_ip}:5985/wsman",
        auth=(settings.ansible_user, settings.ansible_password),
        transport="ntlm",  # ici tu peux laisser ntlm, c'est uniquement pour ce check Python
    )

    elapsed = 0

    while elapsed < timeout:
        try:
            # 1) Vérifier que WinRM répond encore
            ping = session.run_ps("echo ok")
            if ping.status_code != 0:
                raise RuntimeError("WinRM not ready yet")

            # 2) Vérifier que les cmdlets AD fonctionnent
            #    - Get-ADDomain renvoie une erreur tant que le DC n'est pas complètement prêt
            ps_script = r"""
            try {
                Import-Module ActiveDirectory -ErrorAction Stop
                $d = Get-ADDomain -ErrorAction Stop
                Write-Output "AD_READY"
                exit 0
            } catch {
                Write-Output "AD_NOT_READY: $($_.Exception.Message)"
                exit 1
            }
            """

            result = session.run_ps(ps_script)
            output = result.std_out.decode(errors="replace").strip()

            if result.status_code == 0 and "AD_READY" in output:
                logger.info("[WAIT] AD domain is ready on %s (after %ds)", server_ip, elapsed + initial_wait)
                return True

            logger.info(
                "[WAIT] AD not ready yet on %s (%s), retrying in %ds...",
                server_ip,
                output,
                poll_interval,
            )

        except Exception as exc:
            logger.info(
                "[WAIT] Cannot reach %s or AD not ready yet (%s), retrying in %ds...",
                server_ip,
                type(exc).__name__,
                poll_interval,
            )

        time.sleep(poll_interval)
        elapsed += poll_interval

    logger.error("[WAIT] Timeout (%ds) waiting for AD readiness on %s", timeout + initial_wait, server_ip)
    return False

# need to wait for ADWS to be ready because it used in ansible.ad.users
def ansible_deploy_user(user: User, db: Session) -> PlaybookResult:
    ansible = AnsibleService(db=db)

    if not user.domain:
        raise ValueError(f"User '{user.username}' must belong to a domain")

    primary_dc = get_root_dc(user.domain, db)

    if not primary_dc.ip:
        raise ValueError(f"DC '{primary_dc.fqdn}' has no IP address")

    domain = primary_dc.domain
    if not domain:
        raise ValueError(f"DC '{primary_dc.fqdn}' has no domain")

    user_dicts: list[dict[str, str]] = [
        {
            "username": user.username,
            "firstname": user.firstname,
            "lastname": user.lastname,
            "password": user.password,
        }
    ]
    fqdn = primary_dc.fqdn
    base_dn = "DC=" + fqdn.split(".")[-2].lower() + "," + "DC=" + fqdn.split(".")[-1].lower()
    return ansible.add_users(
        server_ip=_bare_ip(primary_dc.ip),
        users=user_dicts,
        base_dn=base_dn,
        domain_fqdn=domain.fqdn,
    )

def get_groups_grouped_by_domain(project: Project) -> dict[Domain, list[Group]]:
    grouped: dict[Domain, list[Group]] = {}
    for forest in project.forests:
        for domain in forest.domains:
            print(domain)
            print(domain.users)
            if domain.groups:
                print("there is this")
                grouped[domain] = list(domain.groups)
    return grouped


def get_groups_not_push_by_domain(project: Project, db: Session) -> dict[Domain, list[Group]]:
    """Retourne, par domaine, les groupes qui n'ont pas encore été poussés dans l'AD
       via le template 'add_groups' (sur le même principe que les users)."""

    groups_by_domain = get_groups_grouped_by_domain(project)
    print("Groups by domain : ", len(groups_by_domain))
    for domain, groups_list in groups_by_domain.items():
        stmt = (
            select(AppliedTemplate)
            .join(Template)
            .where(
                AppliedTemplate.project_id == project.id,
                (AppliedTemplate.status == TemplateStatus.APPLIED)
                | (AppliedTemplate.status == TemplateStatus.ERROR),
                AppliedTemplate.domain_id == domain.id,
                Template.code == "add_groups",
            )
        )
        applied_templates = db.execute(stmt).scalars().all()

        # extraire les noms de groupes déjà poussés
        groupnames_applied: list[str] = []
        for applied in applied_templates:
            if not applied.params:
                continue
            params_json = json.loads(applied.params)
            print(params_json)
            # on décidera que params["groupnames"] contiendra la liste des noms poussés
            groupnames_applied.extend(params_json.get("groupnames", []))

        groups_not_applied = [
            g for g in groups_list if g.name not in groupnames_applied
        ]
        groups_by_domain[domain] = groups_not_applied

    return groups_by_domain

def get_template_for_project(project: Project, db: Session) -> list[AppliedTemplate]:
    stmt = select(AppliedTemplate).where(AppliedTemplate.project_id == project.id)
    return list(db.scalars(stmt).all())


def _create_applied_template(
    db: Session,
    *,
    project_id: int,
    template_code: str,
    domain_id: int | None = None,
    server_id: int | None = None,
    forest_id: int | None = None,
    user_id: int | None = None,
    group_id: int | None = None,
    params: dict | None = None,
) -> AppliedTemplate:
    
    """Create a pending AppliedTemplate record for tracking."""
    template = db.query(Template).filter(Template.code == template_code).first()
    if not template:
        raise ValueError(f"Template '{template_code}' not found in database")

    applied = AppliedTemplate(
        project_id=project_id,
        template_id=template.id,
        domain_id=domain_id,
        server_id=server_id,
        forest_id=forest_id,
        user_id=user_id,
        group_id=group_id,
        params=json.dumps(params) if params else None,
        status=TemplateStatus.PENDING,
    )

    db.add(applied)
    db.commit()
    db.refresh(applied)
    logger.info(
        "[TRACKING] Created AppliedTemplate id=%d (template=%s, status=pending)",
        applied.id,
        template_code,
    )
    return applied


def _update_template_status(
    db: Session,
    applied: AppliedTemplate,
    status: TemplateStatus,
    error: str | None = None,
) -> None:
    """Update the status of an AppliedTemplate after execution."""
    applied.status = status
    db.commit()
    logger.info(
        "[TRACKING] AppliedTemplate id=%d -> status=%s%s",
        applied.id,
        status.value,
        f" (error: {error})" if error else "",
    )


def get_dcs_grouped_by_domain(project: Project) -> dict[Domain, list[Server]]:
    grouped: dict[Domain, list[Server]] = {}
    for forest in project.forests:
        for domain in forest.domains:
            dcs = [s for s in domain.servers if s.is_dc]
            if dcs:
                grouped[domain] = dcs
    return grouped

def is_server_promoted(server: Server, db: Session) -> bool:
    return db.query(
        db.query(AppliedTemplate)
        .join(AppliedTemplate.template)
        .filter(
            AppliedTemplate.server_id == server.id,
            AppliedTemplate.status == TemplateStatus.APPLIED,
            Template.code == "dc_promo",
        )
        .exists()
    ).scalar()

def get_dcs_to_promote(project: Project, db: Session) -> dict[Domain, list[Server]] :
    grouped: dict[Domain, list[Server]] = {}

    for forest in project.forests:
        for domain in forest.domains:
            
            dcs = [s for s in domain.servers if s.is_dc and not is_server_promoted(s, db)]

            if dcs:
                grouped[domain] = dcs

    return grouped

def get_all_domain_in_project(project: Project, db: Session) -> list[Domain]:

    stmt = select(Forest).where(Forest.project_id == project.id)
    list_foret = db.scalars(stmt).all()

    liste_domain = []

    for foret in list_foret:
        stmt = select(Domain).where(Domain.forest_id == foret.id)
        liste_domain.extend(db.scalars(stmt).all())

    return liste_domain


def get_users_grouped_by_domain(project: Project) -> dict[Domain, list[User]]:
    grouped: dict[Domain, list[User]] = {}
    for forest in project.forests:
        for domain in forest.domains:
            if domain.users:
                grouped[domain] = list(domain.users)
    return grouped

def get_users_not_push_by_domain(project: Project, db : Session) -> dict[Domain, list[User]] :
    
    #Récupère tout les templates de type user push
    users = get_users_grouped_by_domain(project)

    for domain, users_list in users.items() :
        stmt = select(AppliedTemplate).join(Template).where(
            AppliedTemplate.project_id == project.id,
            (AppliedTemplate.status == TemplateStatus.APPLIED) | (AppliedTemplate.status == TemplateStatus.ERROR) | (AppliedTemplate.status == TemplateStatus.REVERTED_APPLIED) | (AppliedTemplate.status == TemplateStatus.REVERTED_PENDING),
            AppliedTemplate.domain_id == domain.id,
            Template.code == "add_users",
        )

        liste_applied_template = db.execute(stmt).scalars().all()
        username_applied = []

        for applied_template in liste_applied_template :
            params = applied_template.params
            params_json = json.loads(params)
            users_in_applied_template = params_json["users_list"]
            username_applied.extend(users_in_applied_template)


        usernames_not_applied = [user for user in users_list if user.username not in username_applied]
        users[domain] = usernames_not_applied

    return users


def execute_powershell_winrm(
    server_ip: str,
    powershell_script: str,
    params: dict,
    db: Session,
) -> PlaybookResult:
    ansible = AnsibleService(db=db)

    # Sérialisation correcte : strings entre guillemets, listes/dicts en YAML natif
    vars_lines = []
    for k, v in params.items():
        if isinstance(v, (list, dict)):
            # Valeur complexe : on la sérialise en JSON inline (YAML-compatible)
            vars_lines.append(f"    {k}: {json.dumps(v)}")
        else:
            vars_lines.append(f'    {k}: "{v}"')

    indented_script = textwrap.indent(powershell_script.strip(), "        ")
    playbook_content = "\n".join(
        [
            "- name: Exécuter PowerShell",
            f"  hosts: {server_ip}",
            "  gather_facts: false",
            "  vars:",
            "\n".join(vars_lines),
            "    ansible_connection: winrm",
            "    ansible_winrm_transport: ntlm",
            "    ansible_winrm_server_cert_validation: ignore",
            "    ansible_port: 5985",
            "    ansible_winrm_read_timeout_sec: 120",
            "",
            "  tasks:",
            "    - name: Run PowerShell script",
            "      win_shell: |",
            indented_script,
            "      register: result",
            "",
            "    - name: Debug output",
            "      debug:",
            "        var: result",
        ]
    )

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
        if res.success and res.vm_id:
            srv: Server | None = db.get(Server, res.server_id)
            if srv:
                srv.vm_id = res.vm_id
                srv.status = ServerStatus.APPLIED
                logger.info("[STEP 1] Saved vm_id=%d for server '%s'", res.vm_id, srv.fqdn)
        else:
            srv.status = ServerStatus.ERROR
            logger.warning("[STEP 1] Clone failed or missing vm_id for server_id=%s", res.server_id)

    db.commit()
    logger.info("[STEP 1] All VMs cloned. Waiting 60s for boot...")

    time.sleep(30)

    return deployment_result


def _step_promote_dcs(
    project: Project,
    hypervisor: HypervisorProvider,
    ansible: AnsibleService,
    dcs_by_domain: dict[Domain, list[Server]],
    db: Session,
    deployment_result: DeploymentResult,
) -> DeploymentResult:
    """STEP 2: promouvoir les DC, puis attendre que AD soit réellement prêt."""

    if not dcs_by_domain:
        logger.info("[STEP 2] No DCs to promote, skipping.")
        return deployment_result

    logger.info("[STEP 2] Starting DC promotions across %d domain(s)", len(dcs_by_domain))

    # 1) Envoyer les commandes de promotion sur chaque DC
    for domain, dcs in dcs_by_domain.items():
        logger.info("[STEP 2] Processing domain '%s' (%d DC(s))", domain.fqdn, len(dcs))

        for i, dc in enumerate(dcs):
            if not dc.ip:
                logger.error("[STEP 2] DC '%s' has no IP, skipping", dc.fqdn)
                continue

            is_first_dc = i == 0

            applied = _create_applied_template(
                db,
                project_id=project.id,
                template_code="dc_promo",
                domain_id=domain.id,
                server_id=dc.id,
                forest_id=domain.forest_id,
                params={
                    "target_host": _bare_ip(dc.ip),
                    "dc_hostname": dc.fqdn.split(".")[0],
                    "domain_fqdn": domain.fqdn,
                    "domain_netbios": domain.fqdn.split(".")[0],
                    "is_first_dc": is_first_dc,
                },
            )

            logger.info(
                "[STEP 2] Promoting DC '%s' (is_first_dc=%s) in domain '%s'",
                dc.fqdn,
                is_first_dc,
                domain.fqdn,
            )

            # Le playbook dc_promo fait Install-ADDSForest/DomainController
            # et laisse Windows rebooter tout seul (plus de -NoRebootOnCompletion)
            result = ansible.dc_promote(
                server_ip=_bare_ip(dc.ip),
                dc_hostname=dc.fqdn.split(".")[0],
                domain_fqdn=domain.fqdn,
                domain_netbios=domain.fqdn.split(".")[0],
                is_first_dc=is_first_dc,
            )

            if not result.success:
                _update_template_status(db, applied, TemplateStatus.ERROR, error=result.error)
                logger.error("[STEP 2] DC promotion failed for '%s': %s", dc.fqdn, result.error)
                deployment_result.success = False
                deployment_result.error = result.error
                return deployment_result

            _update_template_status(db, applied, TemplateStatus.APPLIED)
            logger.info("[STEP 2] DC promotion command sent successfully for '%s'", dc.fqdn)

            # IMPORTANT : on NE redémarre PAS la VM via l'hyperviseur ici,
            # c'est Windows qui reboot tout seul après Install-ADDS*

    # 2) Attendre que chaque DC soit réellement prêt côté AD (AD DS + ADWS + Get-ADDomain OK)
    logger.info("[STEP 2] All DC promotion commands sent. Waiting for AD readiness...")

    for _domain, dcs in dcs_by_domain.items():
        for dc in dcs:
            if not dc.ip:
                continue

            ip = _bare_ip(dc.ip)
            logger.info("[STEP 2] Waiting for AD readiness on DC '%s' (%s)...", dc.fqdn, ip)

            if not _wait_for_ad_ready(ip):
                logger.error("[STEP 2] AD not ready on '%s' after timeout", dc.fqdn)
                deployment_result.success = False
                deployment_result.error = f"AD readiness timeout on {dc.fqdn}"
                return deployment_result

            logger.info("[STEP 2] AD is ready on DC '%s'", dc.fqdn)

    return deployment_result


def _step_add_users(
    project: Project,
    ansible: AnsibleService,
    db: Session,
    users_by_domain: dict[Domain, list[User]] | None,
    deployment_result: DeploymentResult,
) -> DeploymentResult:

    if not users_by_domain:
        logger.info("[STEP 3] No users to create, skipping.")
        return deployment_result

    logger.info("[STEP 3] Starting user creation across %d domain(s)", len(users_by_domain))

    for domain, users in users_by_domain.items():
        dc = next((s for s in domain.servers if s.is_dc and s.ip), None)
        if not dc or not dc.ip:
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

        # 1 AppliedTemplate par user, chacun référence son user_id
        applied_list = [
            _create_applied_template(
                db,
                project_id=project.id,
                template_code="add_users",
                domain_id=domain.id,
                server_id=dc.id,
                user_id=u.id,                        # ← référence directe à l'user
                params={
                    "target_host": _bare_ip(dc.ip),
                    "users_list": [u.username],       # ← liste à 1 élément
                    "base_dn": base_dn,
                    "domain_fqdn": domain.fqdn,
                },
            )
            for u in users
        ]

        logger.info(
            "[STEP 3] Adding %d user(s) to domain '%s' via DC '%s'",
            len(users),
            domain.fqdn,
            dc.fqdn,
        )

        # L'appel Ansible reste groupé pour l'efficacité
        result = ansible.add_users(
            server_ip=_bare_ip(dc.ip),
            users=user_dicts,
            base_dn=base_dn,
            domain_fqdn=domain.fqdn,
        )

        if not result.success:
            for applied in applied_list:
                _update_template_status(db, applied, TemplateStatus.ERROR, error=result.error)
            logger.error("[STEP 3] User creation failed on '%s': %s", domain.fqdn, result.error)
            deployment_result.success = False
            deployment_result.error = result.error
            return deployment_result

        for applied in applied_list:
            _update_template_status(db, applied, TemplateStatus.APPLIED)
        logger.info("[STEP 3] Users successfully created on domain '%s'", domain.fqdn)

    return deployment_result


def _step_add_groups(
    project: Project,
    ansible: AnsibleService,
    db: Session,
    groups_by_domain: dict[Domain, list[Group]] | None,
    deployment_result: DeploymentResult,
) -> DeploymentResult:
    if not groups_by_domain:
        logger.info("[STEP ADD_GROUPS] No groups to create, skipping.")
        return deployment_result

    for domain, groups in groups_by_domain.items():
        if not groups:
            continue

        dc = next((s for s in domain.servers if s.is_dc and s.ip), None)
        if not dc or not dc.ip:
            logger.error("[STEP ADD_GROUPS] No reachable DC for '%s', skipping", domain.fqdn)
            continue

        fqdn = dc.fqdn
        base_dn = f"DC={fqdn.split('.')[-2].lower()},DC={fqdn.split('.')[-1].lower()}"

        group_dicts: list[dict[str, Any]] = [
            {"name": g.name, "description": g.description or ""}
            for g in groups
        ]

        # 1 AppliedTemplate par groupe, chacun référence son group_id
        applied_list = [
            _create_applied_template(
                db,
                project_id=project.id,
                template_code="add_groups",
                domain_id=domain.id,
                server_id=dc.id,
                group_id=g.id,                    # ← référence directe au groupe
                params={
                    "target_host": _bare_ip(dc.ip),
                    "groups_list": [g.name],      # ← liste à 1 élément, cohérent avec reverse_content
                    "base_dn": base_dn,
                    "domain_fqdn": domain.fqdn,
                },
            )
            for g in groups
        ]

        logger.info(
            "[STEP ADD_GROUPS] Adding %d group(s) to domain '%s' via DC '%s'",
            len(groups),
            domain.fqdn,
            dc.fqdn,
        )

        # L'appel Ansible reste groupé pour l'efficacité
        result = ansible.add_groups(
            server_ip=_bare_ip(dc.ip),
            groups=group_dicts,
            base_dn=base_dn,
            domain_fqdn=domain.fqdn,
        )

        if not result.success:
            for applied in applied_list:
                _update_template_status(db, applied, TemplateStatus.ERROR, error=result.error)
            logger.error("[STEP ADD_GROUPS] Group creation failed on '%s': %s", domain.fqdn, result.error)
            deployment_result.success = False
            deployment_result.error = result.error
            return deployment_result

        for applied in applied_list:
            _update_template_status(db, applied, TemplateStatus.APPLIED)
        logger.info("[STEP ADD_GROUPS] Groups created on domain '%s'", domain.fqdn)

    return deployment_result


def _step_add_group_members(
    project: Project,
    ansible: AnsibleService,
    db: Session,
    groups_by_domain: dict[Domain, list[Group]] | None,
    deployment_result: DeploymentResult,
) -> DeploymentResult:
    if not groups_by_domain:
        logger.info("[STEP ADD_GROUP_MEMBERS] No memberships to set, skipping.")
        return deployment_result

    for domain, groups in groups_by_domain.items():
        # Garder uniquement les groupes qui ont au moins un membre
        groups_with_members = [
            g for g in groups
            if g.users or g.member_groups
        ]

        if not groups_with_members:
            logger.info(
                "[STEP ADD_GROUP_MEMBERS] No group with members in domain '%s', skipping",
                domain.fqdn
            )
            continue

        dc = next((s for s in domain.servers if s.is_dc and s.ip), None)
        if not dc or not dc.ip:
            logger.error("[STEP ADD_GROUP_MEMBERS] No reachable DC for '%s', skipping", domain.fqdn)
            continue

        memberships: list[dict[str, Any]] = []
        for g in groups_with_members:
            members = (
                [u.username for u in g.users]
                + [mg.name for mg in g.member_groups]
            )
            if members:
                memberships.append({"group_name": g.name, "members": members})

        applied = _create_applied_template(
            db,
            project_id=project.id,
            template_code="add_group_members",
            domain_id=domain.id,
            server_id=dc.id,
            params={
                "target_host": _bare_ip(dc.ip),
                "memberships": memberships,
            },
        )

        logger.info(
            "[STEP ADD_GROUP_MEMBERS] Adding members to %d group(s) on domain '%s'",
            len(memberships),
            domain.fqdn,
        )

        result = ansible.add_group_members(
            server_ip=_bare_ip(dc.ip),
            memberships=memberships,
        )

        if not result.success:
            _update_template_status(db, applied, TemplateStatus.ERROR, error=result.error)
            deployment_result.success = False
            deployment_result.error = result.error
            return deployment_result

        _update_template_status(db, applied, TemplateStatus.APPLIED)
        logger.info("[STEP ADD_GROUP_MEMBERS] Memberships set on domain '%s'", domain.fqdn)

    return deployment_result

def _step_push_vulnerabilities(
    project: Project,
    db: Session,
    deployment_result: DeploymentResult,
) -> DeploymentResult:
    
    liste_templates = get_template_for_project(project, db)
    liste_domain = get_all_domain_in_project(project, db)

    vuln_templates = [
        t
        for t in liste_templates
        if t.template.category != "infrastructure"
        and t.status in (TemplateStatus.PENDING, TemplateStatus.MODIFIED)
    ]

    if not vuln_templates:
        logger.info("[STEP 4] No vulnerability templates to apply, skipping.")
        return deployment_result

    logger.info(
        "[STEP 4] Pushing %d vulnerability template(s) across %d domain(s)",
        len(vuln_templates),
        len(liste_domain),
    )

    has_failure = False

    for domain in liste_domain:
        dc = get_root_dc(domain, db)
        if not dc.ip:
            logger.error("[STEP 4] DC '%s' has no IP, skipping domain '%s'", dc.fqdn, domain.fqdn)
            has_failure = True
            continue

        for applied in vuln_templates:
            if not applied.params:
                logger.error(
                    "[STEP 4] Template '%s' has no params, skipping",
                    applied.template.code,
                )
                _update_template_status(db, applied, TemplateStatus.ERROR, error="Missing params")
                has_failure = True
                continue

            logger.info(
                "[STEP 4] Applying template '%s' on DC '%s' (domain '%s')",
                applied.template.code,
                dc.fqdn,
                domain.fqdn,
            )
            param_vuln = ast.literal_eval(applied.params)
            powershell_script = applied.template.content

            result = execute_powershell_winrm(dc.ip, powershell_script, param_vuln, db)

            if not result.success:
                _update_template_status(db, applied, TemplateStatus.ERROR, error=result.error)
                logger.error(
                    "[STEP 4] Template '%s' failed on '%s': %s",
                    applied.template.code,
                    dc.fqdn,
                    result.error,
                )
                has_failure = True
                continue

            _update_template_status(db, applied, TemplateStatus.APPLIED)
            logger.info(
                "[STEP 4] Template '%s' applied successfully on '%s'",
                applied.template.code,
                dc.fqdn,
            )

    if has_failure:
        deployment_result.success = False
        deployment_result.error = "One or more vulnerability templates failed to apply"

    return deployment_result


def _step_reverse_templates(
    project: Project,
    ansible: AnsibleService,
    db: Session,
    pending_reversed_templates: list[AppliedTemplate],
    deployment_result: DeploymentResult,
) -> DeploymentResult:

    if not pending_reversed_templates:
        logger.info("[STEP REVERSE] No templates to reverse, skipping.")
        return deployment_result

    logger.info("[STEP REVERSE] Reversing %d template(s)", len(pending_reversed_templates))

    liste_domain = get_all_domain_in_project(project, db)
    has_failure = False

    for domain in liste_domain:
        dc = get_root_dc(domain, db)
        if not dc.ip:
            logger.error("[STEP REVERSE] DC '%s' has no IP, skipping domain '%s'", dc.fqdn, domain.fqdn)
            has_failure = True
            continue

        for applied in pending_reversed_templates:

            # Pas de reverse_content défini
            if not applied.template.reverse_content:
                logger.error(
                    "[STEP REVERSE] Template '%s' has no reverse_content, skipping.",
                    applied.template.code,
                )
                _update_template_status(db, applied, TemplateStatus.ERROR, error="Missing reverse_content")
                has_failure = True
                continue

            # Pas de params sauvegardés
            if not applied.params:
                logger.error(
                    "[STEP REVERSE] Template '%s' has no params, skipping.",
                    applied.template.code,
                )
                _update_template_status(db, applied, TemplateStatus.ERROR, error="Missing params")
                has_failure = True
                continue

            param_vuln = json.loads(applied.params)
            powershell_script = applied.template.reverse_content

            logger.info(
                "[STEP REVERSE] Reversing template '%s' on DC '%s' (domain '%s')",
                applied.template.code,
                dc.fqdn,
                domain.fqdn,
            )

            result = execute_powershell_winrm(dc.ip, powershell_script, param_vuln, db)

            if not result.success:
                #_update_template_status(db, applied, TemplateStatus.ERROR, error=result.error)
                logger.error(
                    "[STEP REVERSE] Template '%s' failed on '%s': %s",
                    applied.template.code,
                    dc.fqdn,
                    result.error,
                )
                has_failure = True
                continue

            if applied.template.reverse_type == "deletion" :
                user = applied.user
                if user : 
                    db.delete(user)
                    db.commit()
                group = applied.group
                if group : 
                    db.delete(group)
                    db.commit()

            _update_template_status(db, applied, TemplateStatus.REVERTED_APPLIED)
            logger.info(
                "[STEP REVERSE] Template '%s' reversed successfully on '%s'",
                applied.template.code,
                dc.fqdn,
            )


    if has_failure:
        deployment_result.success = False
        deployment_result.error = "One or more templates failed to reverse"

    return deployment_result

def get_pending_reverted_template(project: Project, db: Session):
    applied_template_reverted = db.query(AppliedTemplate).filter(AppliedTemplate.status == TemplateStatus.REVERTED_PENDING).all()
    
    
    return applied_template_reverted

def build_deployment_steps(
    project: Project,
    all_servers: list[Server],
    hypervisor: HypervisorProvider,
    ansible: AnsibleService,
    db: Session,
) -> list[Callable[[DeploymentResult], DeploymentResult]]:
    steps: list[Callable[[DeploymentResult], DeploymentResult]] = []

    # Serveurs qui n'ont pas encore été clonés
    # servers_to_clone = [s for s in all_servers if s.status != ServerStatus.APPLIED]

    # if servers_to_clone:
    #     steps.append(
    #         lambda r, s=servers_to_clone: _step_clone_vms(project, s, hypervisor, db, r)
    #     )

    # # Serveurs qui n'ont pas été promu
    # servers_to_promote = get_dcs_to_promote(project, db)
    
    # if servers_to_promote :
    #     steps.append(
    #         lambda r: _step_promote_dcs(project, hypervisor, ansible, servers_to_promote, db, r)
    #     )

    # Utilisateur qui n'ont pas encore été pushé
    users_not_pushed = get_users_not_push_by_domain(project, db)
    if any(users_list for users_list in users_not_pushed.values()):
        steps.append(
            lambda r: _step_add_users(project, ansible, db, users_not_pushed, r)
        )

    # Groupes qui n'ont pas encore été pushés
    # STEP : Créer les groupes (sans membres)
    groups_not_pushed = get_groups_not_push_by_domain(project, db)
    if any(gl for gl in groups_not_pushed.values()):
        steps.append(
            lambda r: _step_add_groups(project, ansible, db, groups_not_pushed, r)
        )

    # STEP : Ajouter les membres dans les groupes
    # On réutilise groups_not_pushed : tous les groupes, qu'ils aient des membres ou non.
    # La step filtrera elle-même les groupes sans membres.
    if any(gl for gl in groups_not_pushed.values()):
        steps.append(
            lambda r: _step_add_group_members(project, ansible, db, groups_not_pushed, r)
        )


    # STEP : Récupère les applied_template qui sont en pending_reverted
    find_pending_reverted_template = get_pending_reverted_template(project, db)
    if find_pending_reverted_template :
        steps.append(
            lambda r: _step_reverse_templates(project, ansible, db, find_pending_reverted_template, r)
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
