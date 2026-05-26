import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from adaptive.api.exceptions import DomainNoDCError
from adaptive.api.infrastructure import AnsibleService
from adaptive.api.infrastructure.base import DeploymentResult, HypervisorProvider
from adaptive.api.models.applied_template import AppliedTemplate, TemplateStatus
from adaptive.api.models.domain import Domain
from adaptive.api.models.forest import Forest
from adaptive.api.models.project import Project
from adaptive.api.models.server import Server
from adaptive.api.models.template import Template
from adaptive.api.services.applied_template import _create_applied_template, _update_template_status
from adaptive.api.services.utils import _bare_ip, _wait_for_ad_ready

logger: logging.Logger = logging.getLogger(__name__)


def get_root_dc(domain: Domain, db: Session) -> Server:
    stmt = select(Server).where(Server.domain_id == domain.id, Server.is_dc.is_(True))
    server = db.scalars(stmt).first()
    if not server:
        raise DomainNoDCError(domain.id)
    return server


def get_all_domain_in_project(project: Project, db: Session) -> list[Domain]:
    stmt = select(Forest).where(Forest.project_id == project.id)
    list_foret = db.scalars(stmt).all()

    liste_domain = []

    for foret in list_foret:
        stmt = select(Domain).where(Domain.forest_id == foret.id)
        liste_domain.extend(db.scalars(stmt).all())

    return liste_domain


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


def get_dcs_to_promote(project: Project, db: Session) -> dict[Domain, list[Server]]:
    grouped: dict[Domain, list[Server]] = {}

    for forest in project.forests:
        for domain in forest.domains:
            dcs = [s for s in domain.servers if s.is_dc and not is_server_promoted(s, db)]

            if dcs:
                grouped[domain] = dcs

    return grouped


def _step_promote_dcs(
    project: Project,
    hypervisor: HypervisorProvider,
    ansible: AnsibleService,
    dcs_by_domain: dict[Domain, list[Server]],
    db: Session,
    deployment_result: DeploymentResult,
) -> DeploymentResult:
    """STEP 2: promouvoir les DC, puis attendre que AD soit réellement prêt."""

    logger.info("TEST")
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
